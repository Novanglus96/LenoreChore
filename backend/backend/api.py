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
)
from typing import List, Optional
from django.shortcuts import get_object_or_404
from datetime import date, timedelta, datetime
from ninja.errors import HttpError
from ninja.security import HttpBearer
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator

api = NinjaAPI()
router = Router()
api.title = "LenoreChore API"
api.version = "1.1.6"
api.description = "API documentation for LenoreChore"


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            user = default_token_generator.get_user(token)
        except Exception as e:
            raise HttpError(401, f"Invalid token: {str(e)}")
        return user


class LoginSchema(Schema):
    username: str
    password: str


class LoginUserSchema(Schema):
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
    group_name: str
    group_order: int
    group_color: str


class AreaGroupOut(Schema):
    id: int
    group_name: str
    group_order: int
    group_color: str


class AreaIn(Schema):
    area_name: str
    area_icon: str
    group_id: int


class AreaOut(Schema):
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
    id: int
    name: str


class ChoreIn(Schema):
    chore_name: Optional[str]
    area_id: Optional[int]
    intervalNumber: Optional[int]
    unit: Optional[str]
    active_months: Optional[List[int]]
    effort: Optional[int]
    active: Optional[bool]
    nextDue: Optional[date]
    lastCompleted: Optional[date]
    assignee_id: Optional[int]


class TogglActive(Schema):
    active: bool


class CompleteChore(Schema):
    lastCompleted: date
    completed_by_id: int


class SnoozeChore(Schema):
    nextDue: date


class ClaimChore(Schema):
    assignee_id: Optional[int]


class LastHistoryItem(Schema):
    completed_date: date
    completed_by: str


class ChoreOut(Schema):
    id: int
    chore_name: str
    area_id: int
    area: AreaOut
    active: bool
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


class ChoreOutFull(Schema):
    id: int
    chore_name: str
    area_id: int
    area: AreaOut
    active: bool
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


class HistoryItemIn(Schema):
    completed_date: date
    completed_by: int
    chore_id: int


class HistoryItemOut(Schema):
    id: int
    completed_date: date
    completed_by: CustomUserSchema
    chore: ChoreOutFull


class PaginatedHistoryItems(Schema):
    items: List[HistoryItemOut]
    current_page: int
    total_pages: int
    total_records: int


class OptionIn(Schema):
    vacation_mode: bool
    med_thresh: int
    high_thresh: int


class OptionOut(Schema):
    id: int
    vacation_mode: bool
    med_thresh: int
    high_thresh: int


# The class DatasetObject is a schema representing a Graph Forecast Dataset.
class DatasetObject(Schema):
    backgroundColor: Optional[str]
    data: Optional[List[int]]
    label: Optional[str]


# The class GraphData is a schema representing a graph data object.
class GraphData(Schema):
    labels: List[str]
    datasets: List[DatasetObject]
    title: str


@api.get("/weeklytotals", response=GraphData)
def get_weeklytotals(request, week: Optional[int] = 0):
    """
    The function `get_weeklytotals` retrieves the weekly totals.

    Args:
        request (HttpRequest): The HTTP request object.
        lastweek (bool): Flag to indicate if the totals for last week should be retrieved. Defaults to False.

    Returns:
        GraphData: The graph data with labels and datasets.
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
    return request.user


@api.post("/areagroups")
def create_areagroup(request, payload: AreaGroupIn):
    areagroup = AreaGroup.objects.create(**payload.dict())
    return {"id": areagroup.id}


@api.post("/areas")
def create_area(request, payload: AreaIn):
    area = Area.objects.create(**payload.dict())
    return {"id": area.id}


@api.post("/chores")
def create_chore(request, payload: ChoreIn):
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
    areagroup = get_object_or_404(AreaGroup, id=areagroup_id)
    return areagroup


@api.get("/areas/{area_id}", response=AreaOut)
def get_area(request, area_id: int):
    area = get_object_or_404(Area, id=area_id)
    return area


@api.get("/chores/{chore_id}", response=ChoreOut)
def get_chore(request, chore_id: int):
    chore = get_object_or_404(Chore, id=chore_id)
    return chore


@api.get("/historyitems/{historyitem_id}", response=HistoryItemOut)
def get_historyitem(request, historyitem_id: int):
    historyitem = get_object_or_404(HistoryItem, id=historyitem_id)
    return historyitem


@api.get("/options/{option_id}", response=OptionOut)
def get_option(request, option_id: int):
    option = get_object_or_404(Option, id=option_id)
    return option


@api.get("/areagroups", response=List[AreaGroupOut])
def list_areagroups(request):
    qs = AreaGroup.objects.all()
    return qs


@api.get("/areas", response=List[AreaOut])
def list_areas(request):
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
    qs = Chore.objects.all().order_by(
        "-active", "nextDue", "lastCompleted", "effort", "chore_name", "id"
    )
    if not inactive:
        qs = qs.filter(active=True)
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
            active=chore.active,
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
        )
        chore_list.append(chore_data)

    return chore_list


def calculate_duedays(next_due):
    delta = next_due - date.today()
    return delta.days


@api.get("/historyitems", response=PaginatedHistoryItems)
def list_historyitems(
    request,
    page: Optional[int] = Query(1),
    page_size: Optional[int] = Query(60),
):
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
    qs = Option.objects.all()
    return qs


@api.get("/users", response=List[CustomUserSchema])
def list_users(request):
    qs = CustomUser.objects.all()
    return qs


@api.put("/areagroups/{areagroup_id}")
def update_areagroup(request, areagroup_id: int, payload: AreaGroupIn):
    areagroup = get_object_or_404(AreaGroup, id=areagroup_id)
    areagroup.group_name = payload.group_name
    areagroup.group_order = payload.group_order
    areagroup.group_color = payload.group_color
    areagroup.save()
    return {"success": True}


@api.put("/areas/{area_id}")
def update_area(request, area_id: int, payload: AreaIn):
    area = get_object_or_404(Area, id=area_id)
    area.area_name = payload.area_name
    area.area_icon = payload.area_icon
    area.group_id = payload.group_id
    area.save()
    return {"success": True}


@api.put("/chores/{chore_id}")
def update_chore(request, chore_id: int, payload: ChoreIn):
    chore = get_object_or_404(Chore, id=chore_id)
    chore.chore_name = payload.chore_name
    chore.area_id = payload.area_id
    chore.active = payload.active
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
    chore = get_object_or_404(Chore, id=chore_id)
    chore.active = payload.active
    chore.save()
    return {"success": True}


@api.patch("/chores/snoozechore/{chore_id}")
def snooze_chore(request, chore_id: int, payload: SnoozeChore):
    chore = get_object_or_404(Chore, id=chore_id)
    chore.nextDue = payload.nextDue
    chore.save()
    return {"success": True}


@api.patch("/chores/claimchore/{chore_id}")
def claim_chore(request, chore_id: int, payload: ClaimChore):
    chore = get_object_or_404(Chore, id=chore_id)
    chore.assignee_id = payload.assignee_id
    chore.save()
    return {"success": True}


@api.patch("/chores/completechore/{chore_id}")
def complete_chore(request, chore_id: int, payload: CompleteChore):
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
    historyitem = get_object_or_404(HistoryItem, id=historyitem_id)
    historyitem.completed_date = payload.completed_date
    historyitem.completed_by = payload.completed_by
    historyitem.chore_id = payload.chore_id
    historyitem.save()
    return {"success": True}


@api.put("/options/{option_id}")
def update_option(request, option_id: int, payload: OptionIn):
    option = get_object_or_404(Option, id=option_id)
    option.vacation_mode = payload.vacation_mode
    option.med_thresh = payload.med_thresh
    option.high_thresh = payload.high_thresh
    option.save()
    return {"success": True}


@api.delete("/areagroups/{areagroup_id}")
def delete_areagroup(request, areagroup_id: int):
    areagroup = get_object_or_404(AreaGroup, id=areagroup_id)
    areagroup.delete()
    return {"success": True}


@api.delete("/areas/{area_id}")
def delete_area(request, area_id: int):
    area = get_object_or_404(Area, id=area_id)
    area.delete()
    return {"success": True}


@api.delete("/chores/{chore_id}")
def delete_chore(request, chore_id: int):
    chore = get_object_or_404(Chore, id=chore_id)
    chore.delete()
    return {"success": True}


@api.delete("/historyitems/{historyitem_id}")
def delete_historyitem(request, historyitem_id: int):
    historyitem = get_object_or_404(HistoryItem, id=historyitem_id)
    historyitem.delete()
    return {"success": True}


@router.post("/login")
def login_user(request, payload: LoginSchema):
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
    # Log the user out
    logout(request)
    return {"detail": "Logout successful"}


api.add_router("/auth", router)
