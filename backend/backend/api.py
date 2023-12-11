from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from ninja import NinjaAPI, Schema, Router
from api.models import CustomUser, AreaGroup, Area, Month, Chore, HistoryItem, Option
from typing import List, Optional
from django.shortcuts import get_object_or_404
from datetime import date
from ninja.errors import HttpError
from ninja.security import HttpBearer

api = NinjaAPI()
router = Router()
api.title = "Chores API"
api.version = "1.1.0"
api.description = "API documentation for Chores"


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
    chore_name: str
    area_id: int
    intervalNumber: int
    unit: str
    active_months: List[int]
    effort: int


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
    chore: ChoreOut


class OptionIn(Schema):
    vacation_mode: bool
    med_thresh: int
    high_thresh: int


class OptionOut(Schema):
    id: int
    vacation_mode: bool
    med_thresh: int
    high_thresh: int


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
    historyitem = HistoryItem.objects.create(**payload.dict())
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
    qs = Area.objects.all().order_by('group__group_order', 'area_name')
    return qs


@api.get("/chores", response=List[ChoreOut])
def list_chores(request):
    qs = Chore.objects.all()
    return qs


@api.get("/historyitems", response=List[HistoryItemOut])
def list_historyitems(request):
    qs = HistoryItem.objects.all()
    return qs


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
    chore.active_months = payload.active_months
    chore.assignee = payload.assignee
    chore.effort = payload.effort
    chore.vacationPause = payload.vacationPause
    chore.expand = payload.expand
    chore.save()
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
            'token': token,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'email': user.email,
            'isAdmin': user.is_superuser,
            'male': user.male,
            'id': user.id,
            'user_color': user.user_color,
            'groups': [group.id for group in user.groups.all()]
        }
    else:
        raise HttpError(401, "Invalid credentials")


@router.post("/logout")
def logout_user(request):
    # Log the user out
    logout(request)
    return {'detail': 'Logout successful'}


api.add_router("/auth", router)
