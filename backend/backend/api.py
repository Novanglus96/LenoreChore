from ninja import NinjaAPI, Schema, Router
from ninja.security import django_auth
from backend.sse import notify
from api.models import (
    CustomUser,
    AreaGroup,
    Area,
    Month,
    Chore,
    HistoryItem,
    Option,
    Version,
    PushSubscription,
)
from typing import Dict, List, Optional
from django.conf import settings
from django.shortcuts import get_object_or_404
from datetime import date, time, timedelta
from ninja.errors import HttpError
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Max
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
import importlib.metadata
import platform
import django
from colorfield.validators import COLOR_HEX_RE
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

CACHE_TTL = 15 * 60  # 15 minutes


def invalidate(*keys):
    """Delete one or more exact cache keys."""
    cache.delete_many(keys)


def invalidate_pattern(*patterns):
    """Delete all cache keys matching the given patterns.

    Uses django-redis ``delete_pattern`` when available. Falls back to
    ``cache.clear()`` for non-Redis backends (e.g. LocMemCache).
    """
    for pattern in patterns:
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(pattern)
        else:
            cache.clear()


def invalidate_chores(*extra):
    """Drop every cache a chore write can invalidate.

    There are twelve call sites, and the chore-name index added for the
    "same task everywhere" filter is derived from the chore table -- so a
    rename, a delete or a disable changes it. Bundling them means adding a
    derived cache later cannot silently miss one of those twelve.
    """
    invalidate_pattern("chores:*", *extra)
    invalidate("chorenames")


api = NinjaAPI(auth=django_auth, urls_namespace="api_v2")
router = Router()
api.title = "LenoreChore API"
api.version = "1.5.0-alpha.16"
api.description = "API documentation for LenoreChore"


class VersionOut(Schema):
    """
    Schema to represent a Version.

    Attributes:
        id (int): ID integer. Unique.
        version_number (str): The version of the app.
    """

    id: int
    version_number: str


class VersionDetailsOut(Schema):
    """
    Schema reporting the app version alongside key runtime/dependency
    versions, for confirming what a deployment is actually running.

    Attributes:
        app_version (str): The LenoreChore release version.
        python_version (str): The running Python version.
        django_version (str): The installed Django version.
        packages (Dict[str, str]): Map of key package name to installed version.
    """

    app_version: str
    python_version: str
    django_version: str
    packages: Dict[str, str]


class ProfileIn(Schema):
    """
    Schema to update the logged-in user's own profile.

    Deliberately narrow. The retired DRF `CustomUserSerializer` used
    `fields = "__all__"`, which accepted `is_staff`, `is_superuser`,
    `is_active`, `password` and `email` from the request body. Only the four
    fields the profile form actually edits are settable here, and only ever on
    `request.user` -- there is no user id in the payload or the path.

    Attributes:
        first_name (str): User first name.
        last_name (str): User last name.
        male (bool): Toggle if user is male (selects the avatar).
        user_color (str): Hex colour used to represent the user.
    """

    first_name: str = ""
    last_name: str = ""
    male: bool = True
    user_color: str = ""


class NotificationPrefsIn(Schema):
    """
    Schema to update a user's daily reminder preferences.

    Attributes:
        notify_enabled (bool): Whether daily reminders are enabled.
        notify_time (time): Local wall-clock time to send the reminder.
        notify_timezone (str): IANA timezone the time is interpreted in
            (e.g. "America/New_York"). Empty falls back to the server tz.
    """

    notify_enabled: bool
    notify_time: time
    notify_timezone: str = ""


class NotificationPrefsOut(Schema):
    """
    Schema reporting a user's daily reminder preferences.

    Attributes:
        notify_enabled (bool): Whether daily reminders are enabled.
        notify_time (time): Local wall-clock time to send the reminder.
        notify_timezone (str): IANA timezone the time is interpreted in.
    """

    notify_enabled: bool
    notify_time: time
    notify_timezone: str


class PushSubscriptionIn(Schema):
    """
    Schema to register a Web Push subscription.

    Attributes:
        endpoint (str): The push service endpoint URL.
        p256dh (str): The client public key for payload encryption.
        auth (str): The client auth secret for payload encryption.
    """

    endpoint: str
    p256dh: str
    auth: str


class PushUnsubscribeIn(Schema):
    """
    Schema to remove a Web Push subscription.

    Attributes:
        endpoint (str): The push service endpoint URL to remove.
    """

    endpoint: str


class VapidKeyOut(Schema):
    """
    Schema reporting the public VAPID key for Web Push subscription.

    Attributes:
        public_key (str): The application server public VAPID key.
    """

    public_key: str


class LoginUserSchema(Schema):
    """
    Schema to represent a LoginUserSchema.

    Attributes:
        email (str): User email.
        profile_picture (str): Path to user picutre. Default=None.
        male (bool): Toggle if male or not.
        user_color (str): Hex value of a user color.
        first_name (str): User first name.
        last_name (str): User last name.
        fullname (str): Full name of user.
        is_superuser (bool): Toggle if user is superuser.
        is_staff (bool): Toggle if user is staff.
        is_active (bool): Toggle if user is active.
        groups (List[int]): List of group ids user belongs to.
    """

    email: str
    profile_picture: Optional[str] = None
    male: bool
    user_color: str
    first_name: str
    last_name: str
    fullname: str
    is_superuser: bool
    is_staff: bool
    is_active: bool
    groups: List[int]


class CustomUserSchema(Schema):
    """
    Schema to represent a CustomUserSchema.

    Attributes:
        id (int): ID of the user.
        email (str): Email of the user.
        profile_picture (str): Path to the user profile picture. Default=None.
        male (bool): Toggle if user is male.
        user_color (str): Hex value of a user color.
        first_name (str): User first name.
        last_name (str): User last name.
        fullname (str): Full name of user.
        is_superuser (bool): Toggle if user is superuser.
        is_staff (bool): Toggle if user is staff.
        is_active (bool): Toggle if user is active.
    """

    id: int
    email: str
    profile_picture: Optional[str] = None
    male: bool
    user_color: str
    first_name: str
    last_name: str
    fullname: str
    is_superuser: bool
    is_staff: bool
    is_active: bool
    groups: List[int]
    notify_enabled: bool
    notify_time: time

    @staticmethod
    def resolve_groups(obj):
        """
        Resolve the groups field to a list of group IDs.

        Handles both a CustomUser model (groups is a related manager) and an
        already-serialized value (a list of ids), so the schema survives
        re-validation when used as a nested field (e.g. ChoreOut.assignee).

        Args:
            obj (CustomUser): The user instance being serialized.

        Returns:
            List[int]: List of group IDs the user belongs to.
        """
        groups = getattr(obj, "groups", None)
        if groups is None:
            return []
        if hasattr(groups, "all"):
            return [group.id for group in groups.all()]
        return list(groups)


class ChoreNameOut(Schema):
    """
    Schema to represent a chore name that recurs across the household.

    Attributes:
        chore_name (str): The name itself.
        chore_count (int): How many active chores carry it.
        area_count (int): How many distinct areas those chores span.
    """

    chore_name: str
    chore_count: int
    area_count: int


class AreaGroupIn(Schema):
    """
    Schema to represent an AreaGroupIn.

    Attributes:
        group_name (str): Area group name.
        group_order (int): Area group order index. Optional; on create, a group
            with no order given is appended to the end of the list.
        group_color (str): Hex value of area group color.
    """

    group_name: str
    group_order: Optional[int] = None
    group_color: str


class AreaGroupOut(Schema):
    """
    Schema to represent an AreaGroupOut.

    Attributes:
        id (int): ID of area group.
        group_name (str): Area group name.
        group_order (int): Area group order index.
        group_color (str): Hex value of area group color.
    """

    id: int
    group_name: str
    group_order: int
    group_color: str


class AreaIn(Schema):
    """
    Schema to represent an AreaIn.

    Attributes:
        area_name (str): Area name.
        area_icon (str): Name of area icon.
        group_id (int): ID of group object area belongs to.
    """

    area_name: str
    area_icon: str
    group_id: int


class AreaOut(Schema):
    """
    Schema to represent an AreaOut.

    Attributes:
        id (int): ID of an area.
        area_name (str): Area name.
        area_icon (str): Name of area icon.
        group_id (int): ID of group object area belongs to.
        group (AreaGroupOut): Group object area belongs to.
        dirtiness (int): Percentage of dirtiness for the area.
        dueCount (int): Number of chores due for the area.
        overdueCount (int): Number of chores already past their due date.
        totalCount (int): Total number of chores for the area.
        total_dirtiness (int): Total dirtiness of the area.
    """

    id: int
    area_name: str
    area_icon: str
    # Area.group is null=True with on_delete=SET_DEFAULT, so both of these can
    # legitimately be None. They were declared non-Optional, which meant a single
    # group-less area returned 500 from BOTH /areas and /chores -- the same shape
    # as the two Pydantic-v2 bugs that needed the v1.4.1 hotfix.
    group_id: Optional[int] = None
    group: Optional[AreaGroupOut] = None
    dirtiness: int
    dueCount: int
    overdueCount: int
    totalCount: int
    total_dirtiness: int


class MonthOut(Schema):
    """
    Schema to represent a Month.

    Attributes:
        id (int): ID of the month.
        name (str): Name of the month.
    """

    id: int
    name: str


class ChoreIn(Schema):
    """
    Schema to represent a Chore.

    Attributes:
        chore_name (str): Name of the chore. Optional.
        area_id (int): ID of the area. Optional.
        intervalNumber (int): The repeat interval of the chore. Optional.
        unit (str): The repeat unit of the chore. Optional.
        active_months (List[int]): A list of month ids this chore is active. Optional.
        effort (int): The effort required for this chore. Optional.
        nextDue (date): The date chore is next due. Optional.
        lastCompleted (date): The date chore was last completed. Optional.
        assignee_id (int): ID of the assigned user. Optional.
        status (int): ID of the status. Optional.
    """

    chore_name: Optional[str] = None
    area_id: Optional[int] = None
    intervalNumber: Optional[int] = None
    unit: Optional[str] = None
    active_months: Optional[List[int]] = None
    effort: Optional[int] = None
    nextDue: Optional[date] = None
    lastCompleted: Optional[date] = None
    assignee_id: Optional[int] = None
    status: Optional[int] = None


class TogglActive(Schema):
    """
    Schema to toggle a Chore status.

    Attributes:
        status (int): ID of a status object.
    """

    status: int


class CompleteChore(Schema):
    """
    Schema to complete a Chore object.

    Attributes:
        lastCompleted (date): Date chore was completed.
        completed_by_id (int): ID of the user who completed chore.
    """

    lastCompleted: date
    completed_by_id: int


class SnoozeChore(Schema):
    """
    Schema to snooze a chore object.

    Attributes:
        nextDue (date): Date to set nextDue to.
    """

    nextDue: date


class ClaimChore(Schema):
    """
    Schema to claim a Chore.

    Attributes:
        assignee_id (int): ID of a user to assign to chore. Optional.
    """

    assignee_id: Optional[int] = None


class LastHistoryItem(Schema):
    """
    Schema to represent the last History Item for a chore.

    Attributes:
        completed_date (date): The date the chore was completed.
        completed_by (str): A name of the user who completed the chore.
    """

    completed_date: date
    completed_by: str


class ChoreOut(Schema):
    """
    Schema to represent a Chore.

    Attributes:
        id (int): ID of the chore.
        chore_name (str): Name of the chore.
        area_id (int): ID of an Area object assigned to the chore.
        area (AreaOut): Area object assigned to the chore.
        nextDue (date): Date chore is next due.
        lastCompleted (date): Date chore was last completed.
        intervalNumber (int): Repeat interval for the chore.
        unit (str): Repeat unit for the chore.
        active_months (List[int]): List of Month ids chode is active.
        assignee_id (int): ID of a user assigned to the chore. Default=None.
        effort (int): Effort required for the chore.
        vacationPause (bool): Due days when paused for vacation.
        expand (bool): Toggle expand menu in UI.
        dirtiness (int): Percentage dirty of the chore.
        duedays (int): Days until chore is due.
        last_three_history_items (List[LastHistoryItem]): List of 3 last history items of the chore.
        status (int): Status ID of the chore.
    """

    id: int
    chore_name: str
    area_id: int
    area: AreaOut
    nextDue: date
    lastCompleted: date
    intervalNumber: int
    unit: str
    active_months: List[int]
    assignee_id: Optional[int] = None
    assignee: Optional[CustomUserSchema] = None
    effort: int
    vacationPause: int
    expand: bool
    dirtiness: int
    duedays: int
    last_three_history_items: List[LastHistoryItem]
    status: int


class ChoreOutFull(Schema):
    """
    Schema to represent a Chore with full Assigned User and no History.

    Attributes:
        id (int): ID of the chore.
        chore_name (str): Name of the chore.
        area_id (int): ID of an Area object assigned to the chore.
        area (AreaOut): Area object assigned to the chore.
        nextDue (date): Date chore is next due.
        lastCompleted (date): Date chore was last completed.
        intervalNumber (int): Repeat interval for the chore.
        unit (str): Repeat unit for the chore.
        active_months (List[int]): List of Month ids chode is active.
        assignee_id (int): ID of a user assigned to the chore. Default=None.
        assignee (CustomUserSchema): CustomUser object of the assigned user. Default=None.
        effort (int): Effort required for the chore.
        vacationPause (bool): Due days when paused for vacation.
        expand (bool): Toggle expand menu in UI.
        dirtiness (int): Percentage dirty of the chore.
        duedays (int): Days until chore is due.
        status (int): Status ID of the chore.
    """

    id: int
    chore_name: str
    area_id: int
    area: AreaOut
    nextDue: date
    lastCompleted: date
    intervalNumber: int
    unit: str
    active_months: List[MonthOut]
    assignee_id: Optional[int] = None
    assignee: Optional[CustomUserSchema] = None
    effort: int
    vacationPause: int
    expand: bool
    dirtiness: int
    duedays: int
    status: int


class HistoryItemIn(Schema):
    """
    Schema to represent a HistoryItem.

    Attributes:
        completed_date (date): The date the chore was completed.
        completed_by (str): A name of the user who completed the chore.
        chore_id (int): ID of the chore completed.
    """

    completed_date: date
    completed_by: int
    chore_id: int


class HistoryItemOut(Schema):
    """
    Schema to represent a HistoryItem.

    Attributes:
        id (int): ID of the HistoryItem.
        completed_date (date): The date the chore was completed.
        completed_by (CustomUserSchema): Object of the user who completed chore.
        chore (ChoreOutFull): Object of the chore completed.
    """

    id: int
    completed_date: date
    completed_by: Optional[CustomUserSchema] = None
    chore: ChoreOutFull


class PaginatedHistoryItems(Schema):
    """
    Schema to represent a paginated list of HistoryItems.

    Attributes:
        items (List[HistoryItemOut]): List of HistoryItem objects.
        current_page (int): Page number of current record set.
        total_pages (int): Total number of pages.
        total_records (int): Total numboer of HistoryItems.
    """

    items: List[HistoryItemOut]
    current_page: int
    total_pages: int
    total_records: int


class OptionIn(Schema):
    """
    Schema to represent an Option object.

    Attributes:
        vacation_mode (bool): Toggle for vacation mode.
        med_thresh (int): Medium dirtiness threshold.
        high_thresh (int): High dirtiness threshold.
    """

    vacation_mode: bool
    med_thresh: int
    high_thresh: int


class OptionOut(Schema):
    """
    Schema to represent an Option object.

    Attributes:
        id (int): ID of the Option object.
        vacation_mode (bool): Toggle for vacation mode.
        med_thresh (int): Medium dirtiness threshold.
        high_thresh (int): High dirtiness threshold.
    """

    id: int
    vacation_mode: bool
    med_thresh: int
    high_thresh: int


# The class DatasetObject is a schema representing a Graph Forecast Dataset.
class DatasetObject(Schema):
    """
    Schema to represent a graph DataSet object.

    Attributes:
        backgroundColor (str): Hex value of the graph color. Optional.
        data (List(int)): List of object IDs for the graph.
        label (str): Label for the gaph dataset.
    """

    backgroundColor: Optional[str] = None
    data: Optional[List[int]] = None
    label: Optional[str] = None


# The class GraphData is a schema representing a graph data object.
class GraphData(Schema):
    """
    Schema to represent a GraphData object.

    Attributes:
        labels (List[str]): List of labels for the graph data.
        datasets (List[DatasetObject]): List of DataSetObject objects.
        title (str): Title of the graph.
    """

    labels: List[str]
    datasets: List[DatasetObject]
    title: str


@api.get("/weeklytotals", response=GraphData)
def get_weeklytotals(request, week: int = 0):
    """
    The function `get_weeklytotals` retrieves the weekly totals.

    Endpoint:
        - **Path**: `/api/v2/weeklytotals`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        week (int): Flag to indicate if the totals for last week should be retrieved. Default=0.

    Returns:
        (GraphData): The graph data with labels and datasets.
    """
    cache_key = f"weeklytotals:{week}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # localdate(), not now().date(): see list_chores. With TIME_ZONE set to
    # America/New_York and USE_TZ on, now().date() is the UTC date, so from
    # ~8pm Eastern it is already tomorrow -- and on a Sunday evening that
    # rolled this into next week's window.
    today = timezone.localdate()
    days = week * 7
    start_of_week = (
        today - timedelta(days=today.weekday()) - timedelta(days=days)
    )
    end_of_week = start_of_week + timedelta(days=6)

    datasets = []
    users = CustomUser.objects.all()
    for user in users:
        user_name = None
        if user.first_name and user.first_name != "":
            user_name = user.first_name
        else:
            if len(user.email) > 15:
                if "@" in user.email:
                    parts = user.email.split("@")
                    if len(parts[0]) <= 9:
                        user_name = parts[0] + "@"
                    else:
                        user_name = parts[0][:8] + "*@"
                    if len(parts[1]) <= 5:
                        user_name += parts[1]
                    else:
                        user_name += parts[1][:4] + "*"
                else:
                    user_name = user.email[:14] + "*"
            else:
                user_name = user.email
        # Get records for this week or last week
        records_this_week = HistoryItem.objects.filter(
            completed_by=user,
            completed_date__gte=start_of_week,
            completed_date__lt=start_of_week + timedelta(days=7),
        )

        # Aggregate counts by date
        daily_counts = records_this_week.values("completed_date").annotate(
            count=Count("id")
        )

        # Initialize weekly counts with 0s
        weekly_counts = [0] * 7

        # Map counts to the correct day of the week
        for record in daily_counts:
            day_index = (record["completed_date"] - start_of_week).days
            weekly_counts[day_index] = record["count"]

        dataset_obj = DatasetObject(
            backgroundColor=user.user_color,
            data=weekly_counts,
            label=user_name,
        )
        datasets.append(dataset_obj)
    title = (
        start_of_week.strftime("%m/%d") + " to " + end_of_week.strftime("%m/%d")
    )
    graph = GraphData(labels=labels, datasets=datasets, title=title)
    cache.set(cache_key, graph, CACHE_TTL)
    return graph


@api.get("/me", response=CustomUserSchema)
def me(request):
    """
    The function `me` retrieves the CustomUser object of the logged in user.

    Endpoint:
        - **Path**: `/api/v2/me`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (CustomUserSchema): The CustomUser object of the logged in user.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Not authenticated")
    return request.user


@api.put("/me", response=CustomUserSchema)
def update_me(request, payload: ProfileIn):
    """
    The function `update_me` updates the logged in user's own profile.

    Replaces the retired DRF `PATCH /api/users/{id}/`, which was unauthenticated
    (no DEFAULT_PERMISSION_CLASSES, no permission_classes) and accepted every
    model field including `is_superuser`. This endpoint takes no user id at all
    -- it always writes to `request.user`, so one account can never edit
    another's profile.

    Endpoint:
        - **Path**: `/api/v2/me`
        - **Method**: `PUT`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (ProfileIn): The profile fields to update.

    Returns:
        (CustomUserSchema): The updated CustomUser object.
    """
    user = request.user

    # AbstractUser caps both name fields at 150; without this a longer value
    # reaches the database and surfaces as a 500 rather than a validation error.
    for field, value in (
        ("first name", payload.first_name),
        ("last name", payload.last_name),
    ):
        if len(value) > 150:
            raise HttpError(422, f"{field} must be 150 characters or fewer")

    update_fields = ["first_name", "last_name", "male"]
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.male = payload.male

    # An empty colour means "leave it alone" rather than "blank it", so a client
    # that omits the field cannot silently reset the user's colour.
    if payload.user_color:
        # Reuse the field's own validator rather than restating it. CustomUser
        # .user_color is a ColorField in the default "hex" format, which accepts
        # 6- OR 3-digit values; the hand-written regex here only accepted 6, so
        # a stored 3-digit colour round-tripped from the profile form would have
        # been rejected on save. Importing the library's pattern means the two
        # cannot drift if the field's format ever changes.
        if not COLOR_HEX_RE.match(payload.user_color):
            raise HttpError(422, "user_color must be a hex colour like #E91E63")
        user.user_color = payload.user_color
        update_fields.append("user_color")

    user.save(update_fields=update_fields)

    # The DRF endpoint this replaces did neither of these: other sessions never
    # saw a profile change, and the cached user list kept serving the old name.
    # `/users` caches under a literal "users" key, so delete rather than
    # delete_pattern.
    cache.delete("users")
    notify("users")
    return user


@api.post("/toggle_vacation")
def toggle_vacation(request):
    """
    The function `toggle_vacation` toggles vacation mode.

    Endpoint:
        - **Path**: `/api/v2/toggle_vacation`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (str): Returns success if successful.
    """
    enabling = False
    option = get_object_or_404(Option, id=1)
    if option.vacation_mode:
        enabling = False
    else:
        enabling = True
    option.vacation_mode = not option.vacation_mode
    option.save()
    if enabling:
        chores = Chore.objects.filter(status=0)
        for chore in chores:
            chore.status = 3
            chore.vacationPause = chore.duedays
            chore.save()
    else:
        chores = Chore.objects.filter(status=3)
        for chore in chores:
            chore.status = 0
            chore.nextDue = date.today() + timedelta(days=chore.vacationPause)
            chore.save()
    invalidate("options")
    invalidate_chores()
    invalidate("areas")
    notify("options")
    notify("chores")
    # The state it landed in, not just that something happened. A toggle whose
    # response does not say which way it went leaves every caller guessing --
    # the frontend was about to invert its own stale copy to word a message.
    return {"success": True, "vacation_mode": option.vacation_mode}


@api.post("/areagroups")
def create_areagroup(request, payload: AreaGroupIn):
    """
    The function `create_areagroup` creates an AreaGroup object.

    Endpoint:
        - **Path**: `/api/v2/areagroups`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (AreaGroupIn): An AreaGroup object to create.

    Returns:
        (int): The ID of the newly created AreaGroup object.
    """
    data = payload.model_dump()
    # A new group goes to the end unless the caller asks for a position. The
    # frontend used to send a hardcoded 1 for every group, so ordering was a
    # twelve-way tie broken by whatever the database felt like.
    if not data.get("group_order"):
        highest = AreaGroup.objects.aggregate(Max("group_order"))["group_order__max"]
        data["group_order"] = (highest or 0) + 1
    areagroup = AreaGroup.objects.create(**data)
    invalidate("areagroups")
    notify("areagroups")
    return {"id": areagroup.id}


@api.post("/areas")
def create_area(request, payload: AreaIn):
    """
    The function `create_area` creates an Area object.

    Endpoint:
        - **Path**: `/api/v2/areas`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (AreaIn): Area Object to create.

    Returns:
        (int): ID of the newly created Area object.
    """
    area = Area.objects.create(**payload.model_dump())
    invalidate("areas", "areagroups")
    notify("areas")
    return {"id": area.id}


@api.post("/chores")
def create_chore(request, payload: ChoreIn):
    """
    The function `create_chore` creates a new Chore object.

    Endpoint:
        - **Path**: `/api/v2/chores`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (ChoreIn): Chore object to create.

    Returns:
        (int): ID of the newly created Chore object.
    """
    # Convert active_months IDs into Month instances
    active_months = Month.objects.filter(id__in=payload.active_months)

    # Create the Chore object
    chore = Chore.objects.create(
        chore_name=payload.chore_name,
        area_id=payload.area_id,
        intervalNumber=payload.intervalNumber,
        unit=payload.unit,
        effort=payload.effort,
    )

    # Set the active_months field
    chore.active_months.set(active_months)

    invalidate_chores()
    invalidate("areas")
    notify("chores")
    return {"id": chore.id}


@api.post("/historyitems")
def create_historyitem(request, payload: HistoryItemIn):
    """
    The function `create_historyitem` creates a new HistoryItem object.

    Endpoint:
        - **Path**: `/api/v2/historyitems`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (HistoryItemIn): HistoryItem object to create.

    Returns:
        (int): ID of the newly created HistoryItem object.
    """
    completed_by_id = payload.completed_by
    completed_by_object = get_object_or_404(CustomUser, id=completed_by_id)
    historyitem = HistoryItem.objects.create(
        completed_date=payload.completed_date,
        completed_by=completed_by_object,
        chore_id=payload.chore_id,
    )
    invalidate_chores("weeklytotals:*")
    notify("chores")
    notify("history")
    return {"id": historyitem.id}


@api.get("/areagroups/{areagroup_id}", response=AreaGroupOut)
def get_areagroup(request, areagroup_id: int):
    """
    The function `get_areagroup` retrieves an AreaGroup object.

    Endpoint:
        - **Path**: `/api/v2/areagroups/{areagroup_id}`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        areagroup_id (int): ID of the AreaGroup object to retreive.

    Returns:
        (AreaGroupOut): The AreaGroup object.
    """
    areagroup = get_object_or_404(AreaGroup, id=areagroup_id)
    return areagroup


@api.get("/areas/{area_id}", response=AreaOut)
def get_area(request, area_id: int):
    """
    The function `get_area` retrieves an Area object.

    Endpoint:
        - **Path**: `/api/v2/areas/{area_id}`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        area_id (int): ID of the Area object to retreive.

    Returns:
        (AreaOut): The Area object.
    """
    area = get_object_or_404(Area, id=area_id)
    return area


@api.get("/chores/names", response=List[ChoreNameOut])
def list_chore_names(request):
    """
    The function `list_chore_names` retrieves chore names that appear on more
    than one active chore -- the "same task in several rooms" case, e.g. a
    Dusting that exists separately in every area.

    Only names with two or more active chores are returned: a name carried by a
    single chore cannot be worked through room by room, which is the whole point
    of the filter this feeds.

    Matching is on the name as typed, so it depends on those chores being named
    consistently. A household that writes "Dust" in one area and "Dusting" in
    another gets two entries.

    NOTE: declared BEFORE /chores/{chore_id}. That path converts to int, so a
    request for /chores/names would fail against it with a 422 rather than
    falling through to this one.

    Endpoint:
        - **Path**: `/api/v2/chores/names`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (List[ChoreNameOut]): Recurring chore names, commonest first.
    """
    cached = cache.get("chorenames")
    if cached is not None:
        return cached

    rows = list(
        Chore.objects.filter(status=0)
        .values("chore_name")
        .annotate(
            chore_count=Count("id"),
            area_count=Count("area_id", distinct=True),
        )
        .filter(chore_count__gte=2)
        .order_by("-chore_count", "chore_name")
    )
    cache.set("chorenames", rows, CACHE_TTL)
    return rows


@api.get("/chores/{chore_id}", response=ChoreOut)
def get_chore(request, chore_id: int):
    """
    The function `get_chore` retrieves an Chore object.

    Endpoint:
        - **Path**: `/api/v2/chores/{chore_id}`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        chore_id (int): ID of the Chore object to retreive.

    Returns:
        (ChoreOut): The Chore object.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    return chore


@api.get("/historyitems/{historyitem_id}", response=HistoryItemOut)
def get_historyitem(request, historyitem_id: int):
    """
    The function `get_historyitem` retrieves an HistoryItem object.

    Endpoint:
        - **Path**: `/api/v2/historyitems/{historyitem_id}`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        historyitem_id (int): ID of the HistoryItem object to retreive.

    Returns:
        (HistoryItemOut): The HistoryItem object.
    """
    historyitem = get_object_or_404(HistoryItem, id=historyitem_id)
    return historyitem


@api.get("/options/{option_id}", response=OptionOut)
def get_option(request, option_id: int):
    """
    The function `get_option` retrieves an Option object.

    Endpoint:
        - **Path**: `/api/v2/options/{option_id}`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): ID of the Option object to retreive.

    Returns:
        (OptionOut): The Option object.
    """
    option = get_object_or_404(Option, id=option_id)
    return option


@api.get("/areagroups", response=List[AreaGroupOut])
def list_areagroups(request):
    """
    The function `list_areagroups` retrieves a list of AreaGroup objects.

    Endpoint:
        - **Path**: `/api/v2/areagroups`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (List[AreaGroupOut]): List of AreaGroup objects.
    """
    cached = cache.get("areagroups")
    if cached is not None:
        return cached
    # group_order exists precisely to order this list, and nothing was using it:
    # a bare .all() returns database order, so every group picker in the app was
    # in arbitrary order. group_name breaks ties left over from the era when the
    # frontend hardcoded group_order=1 on every group it created.
    qs = list(AreaGroup.objects.all().order_by("group_order", "group_name"))
    cache.set("areagroups", qs, CACHE_TTL)
    return qs


@api.get("/areas", response=List[AreaOut])
def list_areas(request):
    """
    The function `list_areas` retrieves a list of Area objects.

    Endpoint:
        - **Path**: `/api/v2/areas`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (List[AreaOut]): List of Area objects.
    """
    cached = cache.get("areas")
    if cached is not None:
        return cached
    qs = list(Area.objects.all().order_by("group__group_order", "area_name"))
    cache.set("areas", qs, CACHE_TTL)
    return qs


# Sorts the chore list accepts. Values are the ORM ordering to apply; "dirtiest"
# is None because Chore.dirtiness is a computed Python property, not a column,
# so it cannot be ordered in SQL and is sorted after the list is built.
CHORE_SORTS = {
    "due": ("status", "nextDue", "lastCompleted", "effort", "chore_name", "id"),
    "name": ("chore_name", "id"),
    "effort": ("effort", "nextDue", "chore_name", "id"),
    "dirtiest": None,
}


@api.get("/chores", response=List[ChoreOut])
def list_chores(
    request,
    inactive: bool = False,
    timeframe: Optional[int] = None,
    assignee_id: Optional[int] = None,
    area_id: Optional[int] = None,
    group_id: Optional[int] = None,
    chore_name: Optional[str] = None,
    overdue: bool = False,
    sort: str = "due",
):
    """
    The function `list_chores` retrieves a list of Chore objects.

    Endpoint:
        - **Path**: `/api/v2/chores`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        inactive (bool): Toggle retreiving inactive chores. Default=False.
        timeframe (int): Days from today to retrieve. Retreives all if None. Default=None.
        assignee_id (int): Filter chores by assigned CustomUser ID. Retreives all if None. Default=None.
        area_id (int): Filter chores by Area ID. Retreives all if None. Default=None.
        group_id (int): Filter chores by the AreaGroup their area belongs to. Default=None.
        chore_name (str): Only chores with this name, case-insensitively. Lets one
            task -- dusting, say -- be worked through every area it exists in.
        overdue (bool): Only chores whose due date has already passed. Default=False.
        sort (str): One of `due`, `name`, `effort`, `dirtiest`. Default=`due`.

    Returns:
        (List[ChoreOut]): List of Chore objects.
    """
    if sort not in CHORE_SORTS:
        allowed = ", ".join(sorted(CHORE_SORTS))
        raise HttpError(422, f"Unknown sort '{sort}'. Expected one of: {allowed}")

    # Every parameter has to be in the key. Adding a filter or a sort without
    # extending it serves one request's results to a differently-filtered one.
    cache_key = (
        f"chores:{inactive}:{timeframe}:{assignee_id}:{area_id}"
        f":{group_id}:{chore_name}:{overdue}:{sort}"
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # "dirtiest" still needs a stable base ordering, so ties after the Python
    # sort below fall back to something deterministic rather than to whatever
    # the database returns.
    ordering = CHORE_SORTS[sort] or CHORE_SORTS["due"]
    qs = Chore.objects.all().order_by(*ordering)

    if not inactive:
        qs = qs.filter(status=0)
    if timeframe is not None:
        today = timezone.localdate()
        target_date = today
        if timeframe > 0:
            target_date = today + timedelta(days=timeframe)
        qs = qs.filter(nextDue__lte=target_date)
    if overdue:
        # Strictly before today: something due today is not yet overdue, which
        # is also how ChoreCard's "Due today" vs "N days overdue" reads.
        #
        # localdate(), NOT now().date(). USE_TZ is on and TIME_ZONE is
        # America/New_York, so now().date() is the UTC date -- already tomorrow
        # from about 8pm Eastern. The pre-existing `timeframe` filter above had
        # the same bug: for those hours every evening it matched a day too far,
        # while Chore.duedays and Chore.dirtiness use date.today() and did not.
        qs = qs.filter(nextDue__lt=timezone.localdate())
    if assignee_id is not None:
        qs = qs.filter(assignee_id=assignee_id)
    if area_id is not None:
        qs = qs.filter(area_id=area_id)
    if group_id is not None:
        # Chores reach a group through their area.
        qs = qs.filter(area__group_id=group_id)
    if chore_name:
        # iexact rather than exact: the name is picked from a list the API
        # itself produced, but a filter that silently returns nothing over a
        # capitalisation difference is a bad way to find that out.
        qs = qs.filter(chore_name__iexact=chore_name)
    chore_list = []

    for chore in qs:
        active_months = list(chore.active_months.all())
        active_month_ids = [month.id for month in active_months]
        last_three_query = HistoryItem.objects.filter(chore=chore).order_by(
            "-completed_date"
        )[:3]
        last_three = []
        for item in last_three_query:
            display_name = ""
            if item.completed_by is None:
                # completed_by is SET_NULL on user delete; don't crash on it.
                display_name = "Unknown"
            elif item.completed_by.fullname == " ":
                display_name = item.completed_by.email
            else:
                display_name = item.completed_by.fullname
            last_three_object = LastHistoryItem(
                completed_date=item.completed_date,
                completed_by=display_name,
            )
            last_three.append(last_three_object)
        chore_data = ChoreOut(
            id=chore.id,
            chore_name=chore.chore_name,
            area_id=chore.area_id,
            area=chore.area,  # Assuming AreaOut is a valid representation
            nextDue=chore.nextDue,
            lastCompleted=chore.lastCompleted,
            intervalNumber=chore.intervalNumber,
            unit=chore.unit,
            active_months=active_month_ids,  # Set active_months to the list of IDs
            assignee_id=chore.assignee_id,
            assignee=chore.assignee,
            effort=chore.effort,
            vacationPause=chore.vacationPause,
            expand=chore.expand,
            dirtiness=chore.dirtiness,
            duedays=chore.duedays,
            last_three_history_items=last_three,
            status=chore.status,
        )
        chore_list.append(chore_data)

    if sort == "dirtiest":
        # Chore.dirtiness is computed per chore in Python, so this cannot be an
        # order_by. Sorted here on the built objects, which already carry the
        # value, rather than recomputing it.
        chore_list.sort(key=lambda c: c.dirtiness, reverse=True)

    cache.set(cache_key, chore_list, CACHE_TTL)
    return chore_list


def calculate_duedays(next_due):
    """
    The function `calculate_duedays` calculates the days until due based on a given date.

    Args:
        next_due (date): The chore next due date.

    Returns:
        (int): The number of days until due date.
    """
    delta = next_due - date.today()
    return delta.days


@api.get("/historyitems", response=PaginatedHistoryItems)
def list_historyitems(
    request,
    page: int = 1,
    page_size: int = 60,
):
    """
    The function `list_historyitems` retrieves a list of HistoryItem objects.

    Endpoint:
        - **Path**: `/api/v2/historyitems`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.
        page (int): The page of the paginated History Items to return. Default=1. Optional.
        page_size (int): The page size of paginated History Items. Default=60. Optional.

    Returns:
        (PaginatedHistoryItems): Paginated List of HistoryItem objects.
    """
    qs = HistoryItem.objects.all().order_by("-completed_date", "-id")
    total_pages = 0
    item_list = []
    if len(qs) > 0:
        paginator = Paginator(qs, page_size)
        page_obj = paginator.page(page)
        item_list = list(page_obj.object_list)
        total_pages = paginator.num_pages
    total_records = len(qs)
    paginated_items = PaginatedHistoryItems(
        items=item_list,
        current_page=page,
        total_pages=total_pages,
        total_records=total_records,
    )
    return paginated_items


@api.get("/options", response=List[OptionOut])
def list_options(request):
    """
    The function `list_options` retrieves a list of Option objects.

    Endpoint:
        - **Path**: `/api/v2/options`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (List[OptionOut]): List of Option objects.
    """
    cached = cache.get("options")
    if cached is not None:
        return cached
    qs = list(Option.objects.all())
    cache.set("options", qs, CACHE_TTL)
    return qs


@api.get("/users", response=List[CustomUserSchema])
def list_users(request):
    """
    The function `list_users` retrieves a list of CustomUser objects.

    Endpoint:
        - **Path**: `/api/v2/users`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (List[CustomUserSchema]): List of CustomUser objects.
    """
    cached = cache.get("users")
    if cached is not None:
        return cached
    qs = list(CustomUser.objects.all())
    cache.set("users", qs, CACHE_TTL)
    return qs


@api.put("/areagroups/{areagroup_id}")
def update_areagroup(request, areagroup_id: int, payload: AreaGroupIn):
    """
    The function `update_areagroup` updates a given AreaGroup object.

    Endpoint:
        - **Path**: `/api/v2/areagroups/{areagroup_id}`
        - **Method**: `PUT`

    Args:
        request (HttpRequest): The HTTP request object.
        areagroup_id (int): ID of the AreaGroup object to update.
        payload (AreaGroupIn): AreaGroup object with updates to apply.

    Returns:
        (str): Returns `success` if successful.
    """
    areagroup = get_object_or_404(AreaGroup, id=areagroup_id)
    areagroup.group_name = payload.group_name
    # group_order is optional on the way in (see AreaGroupIn), but the column is
    # a non-null IntegerField -- assigning None unconditionally would turn a
    # rename that omits the order into a 500. Omitting it means "leave it".
    if payload.group_order is not None:
        areagroup.group_order = payload.group_order
    areagroup.group_color = payload.group_color
    areagroup.save()
    invalidate("areagroups")
    notify("areagroups")
    return {"success": True}


@api.put("/areas/{area_id}")
def update_area(request, area_id: int, payload: AreaIn):
    """
    The function `update_area` updates a given Area object.

    Endpoint:
        - **Path**: `/api/v2/areas/{area_id}`
        - **Method**: `PUT`

    Args:
        request (HttpRequest): The HTTP request object.
        area_id (int): ID of the Area object to update.
        payload (AreaIn): Area object with updates to apply.

    Returns:
        (str): Returns `success` if successful.
    """
    area = get_object_or_404(Area, id=area_id)
    area.area_name = payload.area_name
    area.area_icon = payload.area_icon
    area.group_id = payload.group_id
    area.save()
    invalidate("areas", "areagroups")
    notify("areas")
    return {"success": True}


@api.put("/chores/{chore_id}")
def update_chore(request, chore_id: int, payload: ChoreIn):
    """
    The function `update_chore` updates a given Chore object.

    Endpoint:
        - **Path**: `/api/v2/chores/{chore_id}`
        - **Method**: `PUT`

    Args:
        request (HttpRequest): The HTTP request object.
        chore_id (int): ID of the Chore object to update.
        payload (ChoreIn): Chore object with updates to apply.

    Returns:
        (str): Returns `success` if successful.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    chore.chore_name = payload.chore_name
    chore.area_id = payload.area_id
    chore.status = payload.status
    chore.nextDue = payload.nextDue
    chore.lastCompleted = payload.lastCompleted
    chore.intervalNumber = payload.intervalNumber
    chore.unit = payload.unit
    chore.active_months.set(payload.active_months)
    chore.assignee_id = payload.assignee_id
    chore.effort = payload.effort
    chore.save()
    invalidate_chores()
    invalidate("areas")
    notify("chores")
    return {"success": True}


@api.patch("/chores/togglechore/{chore_id}")
def toggle_chore(request, chore_id: int, payload: TogglActive):
    """
    The function `toggle_chore` toggles wether a Chore is active/inactive.

    Endpoint:
        - **Path**: `/api/v2/chores/togglechore/{chore_id}`
        - **Method**: `PATCH`

    Args:
        request (HttpRequest): The HTTP request object.
        chore_id (int): ID of the Chore object to update.
        payload (ToggleActive): ToggleActive schema with status to set for the Chore.

    Returns:
        (str): Returns `success` if successful.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    chore.status = payload.status
    chore.save()
    invalidate_chores()
    invalidate("areas")
    notify("chores")
    return {"success": True}


@api.patch("/chores/snoozechore/{chore_id}")
def snooze_chore(request, chore_id: int, payload: SnoozeChore):
    """
    The function `snooze_chore` updates a given Chore object's next due date.

    Endpoint:
        - **Path**: `/api/v2/chores/snoozechore/{chore_id}`
        - **Method**: `PATCH`

    Args:
        request (HttpRequest): The HTTP request object.
        chore_id (int): ID of the Chore object to update.
        payload (SnoozeChore): SnoozeChore schema with nextDue date to update chore with.

    Returns:
        (str): Returns `success` if successful.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    chore.nextDue = payload.nextDue
    chore.save()
    invalidate_chores()
    invalidate("areas")
    notify("chores")
    return {"success": True}


@api.patch("/chores/claimchore/{chore_id}")
def claim_chore(request, chore_id: int, payload: ClaimChore):
    """
    The function `claim_chore` assigns a given Chore object to a user.

    Endpoint:
        - **Path**: `/api/v2/chores/claimchore/{chore_id}`
        - **Method**: `PATCH`

    Args:
        request (HttpRequest): The HTTP request object.
        chore_id (int): ID of the Chore object to update.
        payload (ClaimChore): ClaimChore schema with a CustomUser ID to assign to chore.

    Returns:
        (str): Returns `success` if successful.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    chore.assignee_id = payload.assignee_id
    chore.save()
    invalidate_chores()
    notify("chores")
    return {"success": True}


@api.patch("/chores/completechore/{chore_id}")
def complete_chore(request, chore_id: int, payload: CompleteChore):
    """
    The function `complete_chore` completes a given Chore object.

    Endpoint:
        - **Path**: `/api/v2/chores/completechore/{chore_id}`
        - **Method**: `PATCH`

    Args:
        request (HttpRequest): The HTTP request object.
        chore_id (int): ID of the Chore object to update.
        payload (CompleteChore): CompleteChore schema to update Chore with.

    Returns:
        (str): Returns `success` if successful.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    chore.lastCompleted = payload.lastCompleted
    if chore.unit == "day(s)":
        chore.nextDue = payload.lastCompleted + relativedelta(
            days=chore.intervalNumber
        )
    elif chore.unit == "week(s)":
        chore.nextDue = payload.lastCompleted + relativedelta(
            weeks=chore.intervalNumber
        )
    elif chore.unit == "month(s)":
        chore.nextDue = payload.lastCompleted + relativedelta(
            months=chore.intervalNumber
        )
    elif chore.unit == "year(s)":
        chore.nextDue = payload.lastCompleted + relativedelta(
            years=chore.intervalNumber
        )
    chore.assignee = None
    chore.save()
    HistoryItem.objects.create(
        completed_date=payload.lastCompleted,
        completed_by_id=payload.completed_by_id,
        chore=chore,
    )
    invalidate_chores("weeklytotals:*")
    invalidate("areas")
    notify("chores")
    notify("history")
    return {"success": True}


@api.put("/historyitems/{historyitem_id}")
def update_historyitem(request, historyitem_id: int, payload: HistoryItemIn):
    """
    The function `update_historyitem` updates a given HistoryItem object.

    Endpoint:
        - **Path**: `/api/v2/historyitems/{historyitem_id}`
        - **Method**: `PUT`

    Args:
        request (HttpRequest): The HTTP request object.
        historyitem_id (int): ID of the HistoryItem object to update.
        payload (HistoryItemIn): HistoryItem object with updates to apply.

    Returns:
        (str): Returns `success` if successful.
    """
    historyitem = get_object_or_404(HistoryItem, id=historyitem_id)
    historyitem.completed_date = payload.completed_date
    historyitem.completed_by = payload.completed_by
    historyitem.chore_id = payload.chore_id
    historyitem.save()
    invalidate_chores("weeklytotals:*")
    notify("chores")
    notify("history")
    return {"success": True}


@api.put("/options/{option_id}")
def update_option(request, option_id: int, payload: OptionIn):
    """
    The function `update_option` updates a given Option object.

    Endpoint:
        - **Path**: `/api/v2/options/{option_id}`
        - **Method**: `PUT`

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): ID of the Option object to update.
        payload (OptionIn): Option object with updates to apply.

    Returns:
        (str): Returns `success` if successful.
    """
    option = get_object_or_404(Option, id=option_id)
    option.vacation_mode = payload.vacation_mode
    option.med_thresh = payload.med_thresh
    option.high_thresh = payload.high_thresh
    option.save()
    invalidate("options")
    notify("options")
    return {"success": True}


@api.delete("/areagroups/{areagroup_id}")
def delete_areagroup(request, areagroup_id: int, reassign_to: Optional[int] = None):
    """
    The function `delete_areagroup` deletes a given AreaGroup object, moving any
    areas that belong to it into another group first.

    Area.group is `null=True, on_delete=SET_DEFAULT, default=1`, which made the
    unguarded delete this replaces unsafe in three separate ways:

    1. Deleting an ordinary group silently moved its areas to group 1 -- no
       warning, no say in the destination.
    2. Deleting group 1 set its own areas' group_id to 1, the row being deleted,
       violating the foreign key.
    3. Any area left group-less returned 500 from /areas and /chores, because
       AreaOut.group was non-Optional. (That schema is fixed too, but an area
       silently losing its group is still wrong.)

    The reassignment is therefore explicit and happens before the delete, so
    SET_DEFAULT never fires at all.

    Endpoint:
        - **Path**: `/api/v2/areagroups/{areagroup_id}`
        - **Method**: `DELETE`

    Args:
        request (HttpRequest): The HTTP request object.
        areagroup_id (int): ID of the AreaGroup object to delete.
        reassign_to (int): ID of the group to move this group's areas into.
            Defaults to the lowest-ordered remaining group.

    Returns:
        (dict): `success`, the destination group id, and how many areas moved.
    """
    areagroup = get_object_or_404(AreaGroup, id=areagroup_id)

    remaining = AreaGroup.objects.exclude(id=areagroup_id).order_by(
        "group_order", "group_name"
    )

    # Areas have to land somewhere, so the last group cannot go.
    if not remaining.exists():
        raise HttpError(
            400,
            "This is the only area group. Create another one before deleting it.",
        )

    if reassign_to is None:
        destination = remaining.first()
    else:
        if reassign_to == areagroup_id:
            raise HttpError(400, "Cannot reassign areas to the group being deleted.")
        destination = get_object_or_404(AreaGroup, id=reassign_to)

    moved = Area.objects.filter(group_id=areagroup_id).update(group=destination)
    areagroup.delete()

    # Reassigning areas changes what /areas and /chores return, so those caches
    # have to go too -- the old version invalidated "areagroups" alone and left
    # every area still reporting its deleted group.
    invalidate("areas", "areagroups")
    invalidate_chores()
    notify("areagroups")
    notify("areas")
    return {"success": True, "reassigned_to": destination.id, "areas_moved": moved}


@api.delete("/areas/{area_id}")
def delete_area(request, area_id: int):
    """
    The function `delete_area` deletes a given Area object.

    Endpoint:
        - **Path**: `/api/v2/areas/{area_id}`
        - **Method**: `DELETE`

    Args:
        request (HttpRequest): The HTTP request object.
        area_id (int): ID of the Area object to delete.

    Returns:
        (str): Returns `success` if successful.
    """
    area = get_object_or_404(Area, id=area_id)
    area.delete()
    invalidate("areas", "areagroups")
    notify("areas")
    return {"success": True}


@api.delete("/chores/{chore_id}")
def delete_chore(request, chore_id: int):
    """
    The function `delete_chore` deletes a given Chore object.

    Endpoint:
        - **Path**: `/api/v2/chores/{chore_id}`
        - **Method**: `DELETE`

    Args:
        request (HttpRequest): The HTTP request object.
        chore_id (int): ID of the Chore object to delete.

    Returns:
        (str): Returns `success` if successful.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    chore.delete()
    invalidate_chores()
    invalidate("areas")
    notify("chores")
    return {"success": True}


@api.delete("/historyitems/{historyitem_id}")
def delete_historyitem(request, historyitem_id: int):
    """
    The function `delete_historyitem` deletes a given HistoryItem object.

    Endpoint:
        - **Path**: `/api/v2/historyitems/{historyitem_id}`
        - **Method**: `DELETE`

    Args:
        request (HttpRequest): The HTTP request object.
        historyitem_id (int): ID of the HistoryItem object to delete.

    Returns:
        (str): Returns `success` if successful.
    """
    historyitem = get_object_or_404(HistoryItem, id=historyitem_id)
    historyitem.delete()
    invalidate_chores("weeklytotals:*")
    notify("chores")
    notify("history")
    return {"success": True}


@api.get("/version/list", response=VersionOut, auth=None)
def list_version(request) -> VersionOut:
    """
    The function `list_version` retrieves the app version number
    from the backend.

    Endpoint:
        - **Path**: `/api/v2/version/list`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        VersionOut: a version object
    """

    try:
        qs = get_object_or_404(Version, id=1)
        return qs
    except Exception as e:
        raise HttpError(500, f"Record retrieval error: {str(e)}")


# Packages reported by /version/details. Add or remove names here as needed.
VERSION_DETAIL_PACKAGES = [
    "django-ninja",
    "djangorestframework",
    "django-redis",
    "django-q2",
    "django-allauth",
    "django-filter",
    "gunicorn",
    "gevent",
    "pillow",
    "arrow",
    "setuptools",
    "wheel",
]


@api.get("/version/details", response=VersionDetailsOut)
def version_details(request):
    """
    The function `version_details` reports the app version alongside the
    running Python/Django versions and a set of key installed package
    versions, so a deployment's full stack can be confirmed from one call.

    Authentication is required, so exact dependency versions are not exposed
    publicly. The unauthenticated `/version/list` endpoint (used by the UI
    update check) is unchanged.

    Endpoint:
        - **Path**: `/api/v2/version/details`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (VersionDetailsOut): App, Python, Django, and package versions.
    """
    packages = {}
    for name in VERSION_DETAIL_PACKAGES:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "not installed"

    version_obj = Version.objects.filter(id=1).first()
    return VersionDetailsOut(
        app_version=version_obj.version_number if version_obj else "unknown",
        python_version=platform.python_version(),
        django_version=django.get_version(),
        packages=packages,
    )


@api.get("/me/notifications", response=NotificationPrefsOut)
def get_notification_prefs(request):
    """
    The function `get_notification_prefs` returns the current user's daily
    reminder preferences.

    Endpoint:
        - **Path**: `/api/v2/me/notifications`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (NotificationPrefsOut): The user's notify_enabled and notify_time.
    """
    return request.user


@api.put("/me/notifications", response=NotificationPrefsOut)
def update_notification_prefs(request, payload: NotificationPrefsIn):
    """
    The function `update_notification_prefs` updates the current user's daily
    reminder preferences.

    Endpoint:
        - **Path**: `/api/v2/me/notifications`
        - **Method**: `PUT`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (NotificationPrefsIn): The new preferences.

    Returns:
        (NotificationPrefsOut): The updated preferences.
    """
    user = request.user
    user.notify_enabled = payload.notify_enabled
    user.notify_time = payload.notify_time
    # Only store a valid IANA timezone; otherwise fall back (empty = server tz).
    tz = payload.notify_timezone or ""
    if tz:
        try:
            ZoneInfo(tz)
        except (ZoneInfoNotFoundError, ValueError):
            tz = ""
    user.notify_timezone = tz

    # If the chosen time is still ahead today (in the user's timezone), clear
    # today's dedup so moving the reminder to a later time fires today rather
    # than waiting until tomorrow.
    tz_obj = ZoneInfo(tz) if tz else ZoneInfo(settings.TIME_ZONE)
    local_now = timezone.now().astimezone(tz_obj)
    if payload.notify_enabled and payload.notify_time > local_now.time():
        user.last_notified_date = None

    user.save(
        update_fields=[
            "notify_enabled",
            "notify_time",
            "notify_timezone",
            "last_notified_date",
        ]
    )
    return user


@api.get("/push/vapid-key", response=VapidKeyOut)
def push_vapid_key(request):
    """
    The function `push_vapid_key` returns the public VAPID key used by the
    browser to create a push subscription.

    Endpoint:
        - **Path**: `/api/v2/push/vapid-key`
        - **Method**: `GET`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (VapidKeyOut): The public VAPID key (empty string if push is not
        configured on this deployment).
    """
    return {"public_key": settings.VAPID_PUBLIC_KEY}


@api.post("/push/subscribe")
def push_subscribe(request, payload: PushSubscriptionIn):
    """
    The function `push_subscribe` registers a Web Push subscription for the
    current user (one per browser/device).

    Endpoint:
        - **Path**: `/api/v2/push/subscribe`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (PushSubscriptionIn): The browser push subscription details.

    Returns:
        (str): Returns `success` if successful.
    """
    PushSubscription.objects.update_or_create(
        endpoint=payload.endpoint,
        defaults={
            "user": request.user,
            "p256dh": payload.p256dh,
            "auth": payload.auth,
        },
    )
    return {"success": True}


@api.post("/push/unsubscribe")
def push_unsubscribe(request, payload: PushUnsubscribeIn):
    """
    The function `push_unsubscribe` removes a Web Push subscription belonging
    to the current user.

    Endpoint:
        - **Path**: `/api/v2/push/unsubscribe`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (PushUnsubscribeIn): The endpoint to remove.

    Returns:
        (str): Returns `success` if successful.
    """
    PushSubscription.objects.filter(
        endpoint=payload.endpoint, user=request.user
    ).delete()
    return {"success": True}


api.add_router("/auth", router)
