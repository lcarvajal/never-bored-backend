from sqlalchemy import and_
from sqlalchemy.orm import Session
from app import models
from app.schemas import user_schema, roadmap_schema, subscription_schema


def add_commit_refresh(db: Session, model):
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

# Users


def create_user(db: Session, user: user_schema.UserCreate):
    db_user = models.user.User(**user.model_dump())
    add_commit_refresh(db, db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.user.User).filter(models.user.User.id == user_id).first()


def get_user_by_uid(db: Session, authentication_service: str, uid: str):
    return db.query(models.user.User).filter(and_(models.user.User.uid == uid, models.user.User.authentication_service == authentication_service)).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.user.User).filter(models.user.User.email == email).first()


def update_user(db: Session, user: user_schema.User):
    db_user = db.query(models.user.User).filter(
        models.user.User.id == user.id).first()

    db_user.name = user.name
    db_user.email = user.email

    if user.payment_gateway_customer_id:
        db_user.payment_gateway_customer_id = user.payment_gateway_customer_id

    if user.payment_gateway_provider:
        db_user.payment_gateway_provider = user.payment_gateway_provider

    add_commit_refresh(db, db_user)
    return db_user


# Roadmaps


def get_roadmap_by_id(db: Session, roadmap_id: int):
    return db.query(models.roadmap.Roadmap).filter(models.roadmap.Roadmap.id == roadmap_id).first()


def get_roadmap_by_id_with_modules(db: Session, roadmap_id: int):
    roadmap = db.query(models.roadmap.Roadmap).filter(
        models.roadmap.Roadmap.id == roadmap_id).first()
    modules = db.query(models.roadmap.Module).filter(
        models.roadmap.Module.roadmap_id == roadmap_id).all()

    roadmap.modules = modules

    return roadmap


def create_roadmap(db: Session, roadmap: roadmap_schema.RoadmapCreate):
    db_roadmap = models.roadmap.Roadmap(**roadmap.model_dump())
    add_commit_refresh(db, db_roadmap)
    return db_roadmap


def create_roadmap_follow(db: Session, roadmap_follow: roadmap_schema.RoadmapFollowCreate):
    db_roadmap_follow = models.roadmap.RoadmapFollow(
        **roadmap_follow.model_dump())
    add_commit_refresh(db, db_roadmap_follow)
    return db_roadmap_follow

# Modules


def create_module(db: Session, module: roadmap_schema.ModuleCreate):
    db_module = models.roadmap.Module(**module.model_dump())
    add_commit_refresh(db, db_module)
    return db_module


def get_module_by_id(db: Session, module_id: int):
    return db.query(models.roadmap.Module).filter(models.roadmap.Module.id == module_id).first()


def get_module_by_id_with_submodules_and_resources(db: Session, module_id: int):
    module = db.query(models.roadmap.Module).filter(
        models.roadmap.Module.id == module_id).first()
    submodules = db.query(models.roadmap.Submodule).filter(
        models.roadmap.Submodule.module_id == module_id).all()

    if len(submodules) > 0:
        for submodule in submodules:
            submodule.resources = db.query(models.roadmap.Resource).filter(
                models.roadmap.Resource.submodule_id == submodule.id).all()

        module.submodules = submodules
    else:
        module.submodules = []

    return module

# Submodules


def create_submodule(db: Session, submodule: roadmap_schema.SubmoduleCreate):
    db_submodule = models.roadmap.Submodule(**submodule.model_dump())
    add_commit_refresh(db, db_submodule)
    return db_submodule


def get_submodule_by_id_with_resources(db: Session, submodule_id: int):
    submodule = db.query(models.roadmap.Submodule).filter(
        models.roadmap.Submodule.id == submodule_id).first()
    submodule.resources = db.query(models.roadmap.Resource).filter(
        models.roadmap.Resource.submodule_id == submodule_id).all()
    return submodule

# Resources


def create_resource(db: Session, resource: roadmap_schema.ResourceCreate):
    db_resource = models.roadmap.Resource(**resource.model_dump())
    add_commit_refresh(db, db_resource)
    return db_resource


# Subscriptions

def create_subscription(db: Session, subscription: subscription_schema.SubscriptionCreate):
    db_subscription = models.subscription.Subscription(
        **subscription.model_dump())
    add_commit_refresh(db, db_subscription)
    return db_subscription


def get_active_subscriptions_for_user(db: Session, user_id: int):
    return db.query(models.subscription.Subscription).filter(and_(models.subscription.Subscription.user_id == user_id, models.subscription.Subscription.status == 'active')).all()


def get_subscription_by_stripe_id(db: Session, subscription_id: str):
    return db.query(models.subscription.Subscription).filter(models.subscription.Subscription.payment_gateway_subscription_id == subscription_id & models.subscription.Subscription.payment_gateway_provider == 'stripe').first()


def update_subscription(db: Session, subscription: subscription_schema.Subscription):
    db_subscription = db.query(models.subscription.Subscription).filter(
        models.subscription.Subscription.id == subscription.id).first()

    db_subscription.status = subscription.status
    db_subscription.current_period_end = subscription.current_period_end

    add_commit_refresh(db, db_subscription)
    return db_subscription


def delete_subscription(db: Session, subscription_id: int):
    db_subscription = db.query(models.subscription.Subscription).filter(
        models.subscription.Subscription.id == subscription_id).delete()
    db_subscription.status = 'deleted'

    add_commit_refresh(db, db_subscription)
    return db_subscription
