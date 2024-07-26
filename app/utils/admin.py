from app.models import user, roadmap
from sqladmin import Admin, ModelView

def configure_admin(app, engine):
  admin = Admin(app, engine)

  class UserAdmin(ModelView, model=user.User):
      column_list = [user.User.id, user.User.name]

  class RoadmapAdmin(ModelView, model=roadmap.Roadmap):
      column_list = [roadmap.Roadmap.id, roadmap.Roadmap.title]

  class RoadmapFollowAdmin(ModelView, model=roadmap.RoadmapFollow):
      column_list = [roadmap.RoadmapFollow.id, roadmap.RoadmapFollow.user_id, roadmap.RoadmapFollow.roadmap_id]

  class ModuleAdmin(ModelView, model=roadmap.Module):
      column_list = [roadmap.Module.id, roadmap.Module.title]

  class SubmoduleAdmin(ModelView, model=roadmap.Submodule):
      column_list = [roadmap.Submodule.id, roadmap.Submodule.title]

  class ResourceAdmin(ModelView, model=roadmap.Resource):
      column_list = [roadmap.Resource.id, roadmap.Resource.title, roadmap.Resource.type, roadmap.Resource.url]

  admin.add_view(UserAdmin)
  admin.add_view(RoadmapAdmin)
  admin.add_view(RoadmapFollowAdmin)
  admin.add_view(ModuleAdmin)
  admin.add_view(SubmoduleAdmin)
  admin.add_view(ResourceAdmin)