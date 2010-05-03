from django.contrib import admin
from rts import models

admin.site.register(models.Player)
admin.site.register(models.Game)
admin.site.register(models.GameStatus)
admin.site.register(models.Map)
admin.site.register(models.MapData)
admin.site.register(models.Ground)
admin.site.register(models.Team)

admin.site.register(models.Obj)
admin.site.register(models.ObjAction)
admin.site.register(models.ObjType)

