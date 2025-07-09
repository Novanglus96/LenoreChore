## CustomUser
### Views
#### ::: backend.api.list_users
#### ::: backend.api.me
#### ::: backend.api.TokenAuth
         options:
            members:
                - authenticate
#### ::: backend.api.login_user
#### ::: backend.api.logout_user
### Schemas
#### ::: backend.api.LoginSchema
#### ::: backend.api.LoginUserSchema
#### ::: backend.api.CustomUserSchema

## AreaGroup
### Views
#### ::: backend.api.create_areagroup
#### ::: backend.api.get_areagroup
#### ::: backend.api.list_areagroups
#### ::: backend.api.update_areagroup
#### ::: backend.api.delete_areagroup
### Schemas
#### ::: backend.api.AreaGroupIn
#### ::: backend.api.AreaGroupOut

## Area
### Views
#### ::: backend.api.create_area
#### ::: backend.api.get_area
#### ::: backend.api.list_areas
#### ::: backend.api.update_area
#### ::: backend.api.delete_area
### Schemas
#### ::: backend.api.AreaIn
#### ::: backend.api.AreaOut

## Month
### Views
### Schemas
#### ::: backend.api.MonthOut

## Chore
### Views
#### ::: backend.api.create_chore
#### ::: backend.api.get_chore
#### ::: backend.api.list_chores
#### ::: backend.api.update_chore
#### ::: backend.api.delete_chore
#### ::: backend.api.toggle_vacation
#### ::: backend.api.calculate_duedays
#### ::: backend.api.toggle_chore
#### ::: backend.api.snooze_chore
#### ::: backend.api.claim_chore
#### ::: backend.api.complete_chore
### Schemas
#### ::: backend.api.ChoreIn
#### ::: backend.api.ChoreOut
#### ::: backend.api.ChoreOutFull
#### ::: backend.api.TogglActive
#### ::: backend.api.CompleteChore
#### ::: backend.api.SnoozeChore
#### ::: backend.api.ClaimChore

## HistoryItem
### Views
#### ::: backend.api.create_historyitem
#### ::: backend.api.get_historyitem
#### ::: backend.api.list_historyitems
#### ::: backend.api.update_historyitem
#### ::: backend.api.delete_historyitem
### Schemas
#### ::: backend.api.HistoryItemIn
#### ::: backend.api.HistoryItemOut
#### ::: backend.api.LastHistoryItem
#### ::: backend.api.PaginatedHistoryItems

## Option
### Views
#### ::: backend.api.get_option
#### ::: backend.api.list_options
#### ::: backend.api.update_option
### Schemas
#### ::: backend.api.OptionIn
#### ::: backend.api.OptionOut

## Version
### Views
#### ::: backend.api.list_version
### Schemas
#### ::: backend.api.VersionOut

## Graphs
### Views
#### ::: backend.api.get_weeklytotals
### Schemas
#### ::: backend.api.DatasetObject
#### ::: backend.api.GraphData