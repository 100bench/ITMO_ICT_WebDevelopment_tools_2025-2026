"""Начальная миграция тайм-менеджера."""

from datetime import date, datetime, time
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260528_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_priority = postgresql.ENUM("low", "medium", "high", "urgent", name="taskpriority", create_type=False)
task_status = postgresql.ENUM("todo", "in_progress", "done", "canceled", name="taskstatus", create_type=False)


def upgrade() -> None:
    task_priority.create(op.get_bind(), checkfirst=True)
    task_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_projects_owner_id"), "projects", ["owner_id"])

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_tags_owner_id"), "tags", ["owner_id"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("priority", task_priority, nullable=False),
        sa.Column("status", task_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_tasks_owner_id"), "tasks", ["owner_id"])
    op.create_index(op.f("ix_tasks_project_id"), "tasks", ["project_id"])

    op.create_table(
        "daily_schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("schedule_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_daily_schedules_owner_id"), "daily_schedules", ["owner_id"])

    op.create_table(
        "task_tags",
        sa.Column("task_id", sa.Integer(), primary_key=True),
        sa.Column("tag_id", sa.Integer(), primary_key=True),
        sa.Column("relation_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "time_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("minutes", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_time_entries_task_id"), "time_entries", ["task_id"])

    op.create_table(
        "schedule_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("schedule_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["schedule_id"], ["daily_schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_schedule_items_schedule_id"), "schedule_items", ["schedule_id"])
    op.create_index(op.f("ix_schedule_items_task_id"), "schedule_items", ["task_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("message", sa.String(length=255), nullable=False),
        sa.Column("notify_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_notifications_owner_id"), "notifications", ["owner_id"])
    op.create_index(op.f("ix_notifications_task_id"), "notifications", ["task_id"])
    seed_demo_data()


# Функция добавляет демонстрационные данные для защиты лабораторной работы.
def seed_demo_data() -> None:
    users = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("email", sa.String),
        sa.column("full_name", sa.String),
        sa.column("password_hash", sa.String),
    )
    projects = sa.table(
        "projects",
        sa.column("id", sa.Integer),
        sa.column("owner_id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
    )
    tags = sa.table(
        "tags",
        sa.column("id", sa.Integer),
        sa.column("owner_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("color", sa.String),
    )
    tasks = sa.table(
        "tasks",
        sa.column("id", sa.Integer),
        sa.column("owner_id", sa.Integer),
        sa.column("project_id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("description", sa.Text),
        sa.column("deadline", sa.DateTime(timezone=True)),
        sa.column("priority", task_priority),
        sa.column("status", task_status),
    )
    task_tags = sa.table(
        "task_tags",
        sa.column("task_id", sa.Integer),
        sa.column("tag_id", sa.Integer),
        sa.column("relation_type", sa.String),
    )
    time_entries = sa.table(
        "time_entries",
        sa.column("id", sa.Integer),
        sa.column("task_id", sa.Integer),
        sa.column("started_at", sa.DateTime(timezone=True)),
        sa.column("finished_at", sa.DateTime(timezone=True)),
        sa.column("minutes", sa.Integer),
        sa.column("note", sa.Text),
    )
    daily_schedules = sa.table(
        "daily_schedules",
        sa.column("id", sa.Integer),
        sa.column("owner_id", sa.Integer),
        sa.column("schedule_date", sa.Date),
        sa.column("title", sa.String),
    )
    schedule_items = sa.table(
        "schedule_items",
        sa.column("id", sa.Integer),
        sa.column("schedule_id", sa.Integer),
        sa.column("task_id", sa.Integer),
        sa.column("start_time", sa.Time),
        sa.column("end_time", sa.Time),
        sa.column("comment", sa.Text),
    )
    notifications = sa.table(
        "notifications",
        sa.column("id", sa.Integer),
        sa.column("owner_id", sa.Integer),
        sa.column("task_id", sa.Integer),
        sa.column("message", sa.String),
        sa.column("notify_at", sa.DateTime(timezone=True)),
        sa.column("is_read", sa.Boolean),
    )

    op.bulk_insert(
        users,
        [
            {
                "id": 1,
                "email": "demo@example.com",
                "full_name": "Demo User",
                "password_hash": "$2b$12$5.XXn3bjmEcHsh8M1ng.peAS4KxJjfyk1qJw28sDLdrE9jzqu34CS",
            }
        ],
    )
    op.bulk_insert(
        projects,
        [
            {
                "id": 1,
                "owner_id": 1,
                "title": "Учеба",
                "description": "Подготовка лабораторных работ по веб-программированию",
            },
            {
                "id": 2,
                "owner_id": 1,
                "title": "Личные задачи",
                "description": "Планирование бытовых и личных задач",
            },
        ],
    )
    op.bulk_insert(
        tags,
        [
            {"id": 1, "owner_id": 1, "name": "Важно", "color": "#ef4444"},
            {"id": 2, "owner_id": 1, "name": "Учеба", "color": "#2563eb"},
            {"id": 3, "owner_id": 1, "name": "Документы", "color": "#16a34a"},
        ],
    )
    op.bulk_insert(
        tasks,
        [
            {
                "id": 1,
                "owner_id": 1,
                "project_id": 1,
                "title": "Подготовить защиту лабораторной 1",
                "description": "Проверить Swagger, Postman collection и объяснение архитектуры",
                "deadline": datetime.fromisoformat("2026-06-02T18:00:00+03:00"),
                "priority": "urgent",
                "status": "in_progress",
            },
            {
                "id": 2,
                "owner_id": 1,
                "project_id": 1,
                "title": "Оформить отчет GitHub Pages",
                "description": "Заполнить index.md и lab1.md для публикации отчета",
                "deadline": datetime.fromisoformat("2026-06-01T20:00:00+03:00"),
                "priority": "high",
                "status": "done",
            },
            {
                "id": 3,
                "owner_id": 1,
                "project_id": 2,
                "title": "Составить план недели",
                "description": "Разложить учебные и личные задачи по дням",
                "deadline": datetime.fromisoformat("2026-06-03T12:00:00+03:00"),
                "priority": "medium",
                "status": "todo",
            },
        ],
    )
    op.bulk_insert(
        task_tags,
        [
            {"task_id": 1, "tag_id": 1, "relation_type": "priority"},
            {"task_id": 1, "tag_id": 2, "relation_type": "topic"},
            {"task_id": 2, "tag_id": 2, "relation_type": "topic"},
            {"task_id": 2, "tag_id": 3, "relation_type": "artifact"},
        ],
    )
    op.bulk_insert(
        time_entries,
        [
            {
                "id": 1,
                "task_id": 1,
                "started_at": datetime.fromisoformat("2026-05-29T10:00:00+03:00"),
                "finished_at": datetime.fromisoformat("2026-05-29T11:30:00+03:00"),
                "minutes": 90,
                "note": "Проверка авторизации и Swagger",
            },
            {
                "id": 2,
                "task_id": 1,
                "started_at": datetime.fromisoformat("2026-05-29T12:00:00+03:00"),
                "finished_at": datetime.fromisoformat("2026-05-29T13:15:00+03:00"),
                "minutes": 75,
                "note": "Подготовка Postman collection",
            },
            {
                "id": 3,
                "task_id": 2,
                "started_at": datetime.fromisoformat("2026-05-28T18:00:00+03:00"),
                "finished_at": datetime.fromisoformat("2026-05-28T19:00:00+03:00"),
                "minutes": 60,
                "note": "Заполнение отчета",
            },
        ],
    )
    op.bulk_insert(
        daily_schedules,
        [
            {
                "id": 1,
                "owner_id": 1,
                "schedule_date": date(2026, 5, 29),
                "title": "День подготовки к защите",
            }
        ],
    )
    op.bulk_insert(
        schedule_items,
        [
            {
                "id": 1,
                "schedule_id": 1,
                "task_id": 1,
                "start_time": time(10, 0),
                "end_time": time(11, 30),
                "comment": "Проверить защищенные эндпоинты",
            },
            {
                "id": 2,
                "schedule_id": 1,
                "task_id": 2,
                "start_time": time(18, 0),
                "end_time": time(19, 0),
                "comment": "Показать отчет на GitHub Pages",
            },
        ],
    )
    op.bulk_insert(
        notifications,
        [
            {
                "id": 1,
                "owner_id": 1,
                "task_id": 1,
                "message": "До дедлайна лабораторной осталось меньше суток",
                "notify_at": datetime.fromisoformat("2026-06-01T18:00:00+03:00"),
                "is_read": False,
            },
            {
                "id": 2,
                "owner_id": 1,
                "task_id": 2,
                "message": "Проверить ссылки в отчете",
                "notify_at": datetime.fromisoformat("2026-05-31T12:00:00+03:00"),
                "is_read": True,
            },
        ],
    )

    for table_name in [
        "users",
        "projects",
        "tags",
        "tasks",
        "time_entries",
        "daily_schedules",
        "schedule_items",
        "notifications",
    ]:
        op.execute(sa.text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1)) FROM {table_name}"))


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_task_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_owner_id"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_schedule_items_task_id"), table_name="schedule_items")
    op.drop_index(op.f("ix_schedule_items_schedule_id"), table_name="schedule_items")
    op.drop_table("schedule_items")
    op.drop_index(op.f("ix_time_entries_task_id"), table_name="time_entries")
    op.drop_table("time_entries")
    op.drop_table("task_tags")
    op.drop_index(op.f("ix_daily_schedules_owner_id"), table_name="daily_schedules")
    op.drop_table("daily_schedules")
    op.drop_index(op.f("ix_tasks_project_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_owner_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_tags_owner_id"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_projects_owner_id"), table_name="projects")
    op.drop_table("projects")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    task_status.drop(op.get_bind(), checkfirst=True)
    task_priority.drop(op.get_bind(), checkfirst=True)
