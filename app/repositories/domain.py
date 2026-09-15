"""Файл содержит запросы к основным сущностям тайм-менеджера."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import DailySchedule, Notification, ParsedPage, Project, ScheduleItem, Tag, Task, TaskTag, TimeEntry


def get_project(db: Session, project_id: int, owner_id: int) -> Project | None:
    return db.scalar(select(Project).where(Project.id == project_id, Project.owner_id == owner_id))


def list_projects(db: Session, owner_id: int) -> list[Project]:
    return list(db.scalars(select(Project).where(Project.owner_id == owner_id).order_by(Project.id)))


def get_task(db: Session, task_id: int, owner_id: int, detailed: bool = False) -> Task | None:
    query = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    if detailed:
        query = query.options(
            selectinload(Task.project),
            selectinload(Task.tag_links).selectinload(TaskTag.tag),
            selectinload(Task.time_entries),
        )
    return db.scalar(query)


def list_tasks(db: Session, owner_id: int) -> list[Task]:
    return list(db.scalars(select(Task).where(Task.owner_id == owner_id).order_by(Task.deadline, Task.id)))


def get_tag(db: Session, tag_id: int, owner_id: int) -> Tag | None:
    return db.scalar(select(Tag).where(Tag.id == tag_id, Tag.owner_id == owner_id))


def list_tags(db: Session, owner_id: int) -> list[Tag]:
    return list(db.scalars(select(Tag).where(Tag.owner_id == owner_id).order_by(Tag.name)))


def get_task_tag(db: Session, task_id: int, tag_id: int) -> TaskTag | None:
    return db.get(TaskTag, {"task_id": task_id, "tag_id": tag_id})


def get_time_entry(db: Session, entry_id: int, owner_id: int) -> TimeEntry | None:
    return db.scalar(select(TimeEntry).join(Task).where(TimeEntry.id == entry_id, Task.owner_id == owner_id))


def list_time_entries(db: Session, owner_id: int) -> list[TimeEntry]:
    return list(db.scalars(select(TimeEntry).join(Task).where(Task.owner_id == owner_id).order_by(TimeEntry.started_at)))


def get_schedule(db: Session, schedule_id: int, owner_id: int) -> DailySchedule | None:
    return db.scalar(
        select(DailySchedule)
        .where(DailySchedule.id == schedule_id, DailySchedule.owner_id == owner_id)
        .options(selectinload(DailySchedule.items).selectinload(ScheduleItem.task))
    )


def list_schedules(db: Session, owner_id: int) -> list[DailySchedule]:
    return list(
        db.scalars(
            select(DailySchedule)
            .where(DailySchedule.owner_id == owner_id)
            .options(selectinload(DailySchedule.items).selectinload(ScheduleItem.task))
            .order_by(DailySchedule.schedule_date)
        )
    )


def get_notification(db: Session, notification_id: int, owner_id: int) -> Notification | None:
    return db.scalar(
        select(Notification)
        .where(Notification.id == notification_id, Notification.owner_id == owner_id)
        .options(selectinload(Notification.task))
    )


def list_notifications(db: Session, owner_id: int) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.owner_id == owner_id)
            .options(selectinload(Notification.task))
            .order_by(Notification.notify_at)
        )
    )


def get_parsed_page(db: Session, page_id: int, owner_id: int) -> ParsedPage | None:
    return db.scalar(select(ParsedPage).where(ParsedPage.id == page_id, ParsedPage.owner_id == owner_id))


def list_parsed_pages(db: Session, owner_id: int) -> list[ParsedPage]:
    query = (
        select(ParsedPage)
        .where(ParsedPage.owner_id == owner_id)
        .order_by(ParsedPage.fetched_at.desc(), ParsedPage.id.desc())
    )
    return list(db.scalars(query))


def time_by_task(db: Session, owner_id: int) -> list[tuple[int, str, int]]:
    return list(
        db.execute(
            select(Task.id, Task.title, func.coalesce(func.sum(TimeEntry.minutes), 0))
            .outerjoin(TimeEntry)
            .where(Task.owner_id == owner_id)
            .group_by(Task.id, Task.title)
            .order_by(Task.id)
        )
    )


def time_by_project(db: Session, owner_id: int) -> list[tuple[int | None, str | None, int]]:
    return list(
        db.execute(
            select(Project.id, Project.title, func.coalesce(func.sum(TimeEntry.minutes), 0))
            .select_from(Task)
            .outerjoin(Project, Project.id == Task.project_id)
            .outerjoin(TimeEntry, TimeEntry.task_id == Task.id)
            .where(Task.owner_id == owner_id)
            .group_by(Project.id, Project.title)
            .order_by(Project.id)
        )
    )
