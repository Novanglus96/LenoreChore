from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from ninja import NinjaAPI, Schema, Router, Query
from api.models import (
    CustomUser,
    AreaGroup,
    Area,
    Month,
    Chore,
    HistoryItem,
    Option,
    Version,
)
from typing import List, Optional
from django.shortcuts import get_object_or_404
from datetime import date, timedelta, datetime
from ninja.errors import HttpError
from ninja.security import HttpBearer
from dateutil.relativedelta import relativedelta
from django.db.models import Count, F
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator

api = NinjaAPI()
router = Router()
api.title = "LenoreChore API"
api.version = "1.2.23"
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


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        """
        The function `authenticate` authenticates a user.

        Args:
            self ():
            request ():
            token ():

        Returns:
            user (token): Returns a user token.
        """
        try:
            user = default_token_generator.get_user(token)
        except Exception as e:
            raise HttpError(401, f"Invalid token: {str(e)}")
        return user


class LoginSchema(Schema):
    """
    Schema to represent a LoginSchema.

    Attributes:
        username (str): Username string.
        password (str): Password string.
    """

    username: str
    password: str


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
    profile_picture: str = None
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
    profile_picture: str = None
    male: bool
    user_color: str
    first_name: str
    last_name: str
    fullname: str
    is_superuser: bool
    is_staff: bool
    is_active: bool


class AreaGroupIn(Schema):
    """
    Schema to represent an AreaGroupIn.

    Attributes:
        group_name (str): Area group name.
        group_order (int): Area group order index.
        group_color (str): Hex value of area group color.
    """

    group_name: str
    group_order: int
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
        totalCount (int): Total number of chores for the area.
        total_dirtiness (int): Total dirtiness of the area.
    """

    id: int
    area_name: str
    area_icon: str
    group_id: int
    group: AreaGroupOut
    dirtiness: int
    dueCount: int
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

    chore_name: Optional[str]
    area_id: Optional[int]
    intervalNumber: Optional[int]
    unit: Optional[str]
    active_months: Optional[List[int]]
    effort: Optional[int]
    nextDue: Optional[date]
    lastCompleted: Optional[date]
    assignee_id: Optional[int]
    status: Optional[int]


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

    assignee_id: Optional[int]


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
    assignee_id: Optional[int]
    assignee: CustomUserSchema = None
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
    assignee_id: Optional[int]
    assignee: CustomUserSchema = None
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
    completed_by: CustomUserSchema
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

    backgroundColor: Optional[str]
    data: Optional[List[int]]
    label: Optional[str]


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
def get_weeklytotals(request, week: Optional[int] = 0):
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
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    today = timezone.now().date()
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
    return request.user


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
    return {"success": True}


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
    areagroup = AreaGroup.objects.create(**payload.dict())
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
    area = Area.objects.create(**payload.dict())
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
    qs = AreaGroup.objects.all()
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
    qs = Area.objects.all().order_by("group__group_order", "area_name")
    return qs


@api.get("/chores", response=List[ChoreOut])
def list_chores(
    request,
    inactive: bool = False,
    timeframe: int = None,
    assignee_id: int = None,
    area_id: int = None,
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

    Returns:
        (List[ChoreOut]): List of Chore objects.
    """
    qs = Chore.objects.all().order_by(
        "status", "nextDue", "lastCompleted", "effort", "chore_name", "id"
    )
    if not inactive:
        qs = qs.filter(status=0)
    if timeframe is not None:
        today = timezone.now().date()
        target_date = today
        if timeframe > 0:
            target_date = today + timedelta(days=timeframe)
        qs = qs.filter(nextDue__lte=target_date)
    if assignee_id is not None:
        qs = qs.filter(assignee_id=assignee_id)
    if area_id is not None:
        qs = qs.filter(area_id=area_id)
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
            if item.completed_by.fullname == " ":
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
    page: Optional[int] = Query(1),
    page_size: Optional[int] = Query(60),
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
    qs = Option.objects.all()
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
    qs = CustomUser.objects.all()
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
    areagroup.group_order = payload.group_order
    areagroup.group_color = payload.group_color
    areagroup.save()
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
    return {"success": True}


@api.delete("/areagroups/{areagroup_id}")
def delete_areagroup(request, areagroup_id: int):
    """
    The function `delete_areagroup` deletes a given AreaGroup object.

    Endpoint:
        - **Path**: `/api/v2/areagroups/{areagroup_id}`
        - **Method**: `DELETE`

    Args:
        request (HttpRequest): The HTTP request object.
        areagroup_id (int): ID of the AreaGroup object to delete.

    Returns:
        (str): Returns `success` if successful.
    """
    areagroup = get_object_or_404(AreaGroup, id=areagroup_id)
    areagroup.delete()
    return {"success": True}


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
    return {"success": True}


@router.post("/login")
def login_user(request, payload: LoginSchema):
    """
    The function `login_user` logs in a user.

    Endpoint:
        - **Path**: `/api/v2/login`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.
        payload (LoginSchema): A username and password.

    Returns:
        (object): Returns a user object with token.
    """
    username = payload.username
    password = payload.password

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)

        # Retrieve or create a token for the authenticated user
        token = default_token_generator.make_token(user)

        return {
            "token": token,
            "firstname": user.first_name,
            "lastname": user.last_name,
            "email": user.email,
            "isAdmin": user.is_superuser,
            "male": user.male,
            "id": user.id,
            "user_color": user.user_color,
            "groups": [group.id for group in user.groups.all()],
        }
    else:
        raise HttpError(401, "Invalid credentials")


@router.post("/logout")
def logout_user(request):
    """
    The function `logout_user` logs out.

    Endpoint:
        - **Path**: `/api/v2/logout`
        - **Method**: `POST`

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        (str): Returns `detail: Logout successful` if successful.
    """
    # Log the user out
    logout(request)
    return {"detail": "Logout successful"}


@api.get("/version/list", response=VersionOut)
def list_version(request):
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


api.add_router("/auth", router)
