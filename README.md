# Данное описание относится к материнскому репозиторию, продублирован здесь для ознакомления.

# pg_git_project_ready — Docker‑сборка для Git‑синхронизируемых cron‑задач на Python + PostgreSQL

Готовая инфраструктура, где код задач хранится в **отдельном Git‑репозитории**, а контейнеры:
- **подтягивают код** по расписанию (sidecar `git-sync`);
- **устанавливают/обновляют зависимости** при изменении `requirements.txt` (по хэшу);
- **перезапускают cron‑расписание** при изменении `crontab.txt` (по хэшу);
- пишут вывод задач в STDOUT (видно через `docker compose logs`).

Репозиторий со скриптами (пример): `shurikovyy/docker_test` — в корне лежит `requirements.txt`, в каталоге `app/` — `crontab.txt` и скрипты. :contentReference[oaicite:1]{index=1}

---

## Быстрый старт

1. Клонируйте инфраструктуру и перейдите в каталог:

   ```bash
   git clone https://github.com/shurikovyy/pg_git_project_ready.git
   cd pg_git_project_ready
   ```

2. Создайте `.env` на основе `.env.example` и заполните минимум:

   ```ini
   POSTGRES_USER=pguser
   POSTGRES_PASSWORD=pgpassword
   POSTGRES_DB=pgdb
   # Git-репозиторий со скриптами:
   GIT_SYNC_REPO=https://github.com/<owner>/<repo>.git
   GIT_SYNC_BRANCH=main
   # Для приватного репо по HTTPS — используйте PAT:
   GIT_SYNC_USERNAME=<github_username>
   GIT_SYNC_PASSWORD=<github_pat>
   # Таймзона для cron
   TZ=Europe/Amsterdam
   ```

3. Поднимите стек:

   ```bash
   docker compose up -d --build
   ```

4. Смотрите логи:

   ```bash
   docker compose logs -f git-sync
   docker compose logs -f app
   ```

---

## Структура репозитория

* `docker-compose.yml` — описание сервисов.
* `Dockerfile` — образ приложения (`app`).
* `entrypoint.sh` — логика ожидания кода, установки зависимостей по хэшу и запуска supercronic.
* `git-sync/` — образ сайдкара для синхронизации Git.
* `initdb/` — SQL‑скрипты для первичной инициализации БД.
* `postgresql.conf` — кастомная конфигурация PostgreSQL.
* `requirements.txt` — зависимости образа `app` (опционально, для базовых нужд).
* `.env.example` — шаблон переменных окружения.


## `pg_git_project_ready` (инфраструктура)

```
pg_git_project_ready/
├─ docker-compose.yml            # стек: db, git-sync, app; маунты, env, healthchecks
├─ Dockerfile                    # образ сервиса app (python + supercronic)
├─ entrypoint.sh                 # логика ожидания кода, хэши req/cron, автоустановка, перезапуск cron
├─ git-sync/
│  ├─ Dockerfile                # образ sidecar'а git-sync (alpine/debian)
│  └─ entrypoint.sh             # clone/fetch/reset с поддержкой HTTPS(PAT)/SSH
├─ initdb/
│  └─ init.sql                  # первичная инициализация БД (CREATE TABLE IF NOT EXISTS ...)
├─ postgresql.conf              # кастомный конфиг PostgreSQL (монтируется RO)
├─ requirements.txt             # базовые зависимости образа app (на этапе сборки, опционально)
├─ .env.example                 # пример переменных окружения (копируешь в .env)
└─ README.md                    # документация (быстрый старт, сервисы, хэши и т.д.)
```

> Примечание: **том состояния** (с хэшами `requirements.sha256` и `crontab.sha256`) — это *именованный volume* Docker, в репозитории его нет. В рантайме он монтируется в контейнер `app` как:

```
/var/lib/app-state/requirements.sha256
/var/lib/app-state/crontab.sha256
/var/lib/app-state/crontab.runtime.txt
```

## `docker_test` (репозиторий со скриптами, тянется git-sync)

```
docker_test/
├─ requirements.txt              # runtime-зависимости скриптов; по нему считаем хэш и ставим пакеты
└─ app/
   ├─ crontab.txt               # расписание supercronic; по нему считаем хэш и перезапускаем cron
   └─ scripts/
      ├─ hello.py               # пример задачи
      ├─ populate_test_data.py  # вставка тестовых строк в БД
      └─ ...                    # ваши другие скрипты
```

---

## Репозиторий со скриптами (внешний)

Ожидаемая структура (по умолчанию):

```
requirements.txt
app/
  crontab.txt
  scripts/
    *.py
```

* По умолчанию `app` ищет:
  `REQ_FILE=/app/project/docker_test/requirements.txt`
  `CRON_FILE=/app/project/docker_test/app/crontab.txt`
* Если у вас другая структура — переопределите через переменные окружения сервиса `app` (см. ниже).
  В примере репозитория `docker_test` `requirements.txt` действительно лежит в корне, а `app/` существует. ([GitHub][2])

---

## Сервисы и тонкости работы

### 1) `db` (PostgreSQL)

* Официальный образ Postgres.
* Инициализация: всё из `initdb/` исполняется **один раз** при создании пустого тома данных.
* Конфигурация: `postgresql.conf` монтируется read‑only и применяется при старте.
* Переменные из `.env`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
* **Данные** живут в именованном томе (например, `pgdata`). `docker compose down -v` удалит его.

### 2) `git-sync` (сайдкар)

* Параметры: `GIT_SYNC_REPO`, `GIT_SYNC_BRANCH` (по умолчанию `main`), `GIT_SYNC_WAIT` (интервал, сек).
* Работает в цикле: первичный `clone` → периодические `fetch` + `reset --hard`.
* Кладёт рабочее дерево в именованный том (например, `dags`), *не пишет* в глобальный git‑config на read‑only ФС (в нашем варианте безопасно прокидывается `safe.directory` в вызовах `git`).
* Аутентификация: HTTPS + PAT через `GIT_SYNC_USERNAME`/`GIT_SYNC_PASSWORD` или SSH‑ключ (рекомендуется; монтируется read‑only).

### 3) `app` (Python + supercronic)

* На старте:

  1. **Ждёт** появления `requirements.txt` из синхронизированного кода.
  2. Считает SHA‑256 `requirements.txt`. Если хэша ещё нет или он **изменился** — выполняет:

     ```
     pip install --user -r <requirements.txt>
     ```

     и сохраняет хэш в персистентном **томе состояния**.
  3. Готовит `crontab` и запускает `supercronic`.
* В цикле (каждые `POLL_SEC` сек):

  * сравнивает хэш `requirements.txt`: при изменении — останавливает supercronic, доустанавливает зависимости, обновляет хэш, снова запускает supercronic;
  * сравнивает хэш `crontab.txt`: при изменении — перегенерирует runtime‑crontab (без записи в read‑only код) и перезапускает supercronic.
* Хэши хранятся в **персистентном томе состояния** (например, монтируется в `/var/lib/app-state`), чтобы не переустанавливать зависимости без изменений.
* Подключение к БД: используйте либо `DATABASE_URL=postgresql://USER:PASSWORD@db:5432/DBNAME`, либо стандартные `PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD` — пробросить их в `environment`.

> Замечание: если в `docker-compose.yml` ещё нет тома состояния (например, `app_state`) — добавьте его и примонтируйте в `/var/lib/app-state`.

---

## Переменные окружения (основные)

**`git-sync`:**

* `GIT_SYNC_REPO` — URL (HTTPS или SSH).
* `GIT_SYNC_BRANCH` — ветка (по умолчанию `main`).
* `GIT_SYNC_WAIT` — интервал опроса, сек.
* `GIT_SYNC_USERNAME` / `GIT_SYNC_PASSWORD` — для HTTPS + PAT (по желанию).

**`app`:**

* `REQ_FILE` — путь к `requirements.txt` в смонтированном коде (по умолчанию `/app/project/docker_test/requirements.txt`).
* `CRON_FILE` — путь к `crontab.txt` (по умолчанию `/app/project/docker_test/app/crontab.txt`).
* `POLL_SEC` — частота проверки хэшей, сек (например, `15`).
* `STATE_DIR` — каталог хранения хэшей (по умолчанию `/var/lib/app-state`).
* Подключение к БД: `DATABASE_URL` **или** `PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD`.
* `TZ` — таймзона для cron (например, `Europe/Amsterdam`).

---

## Cron‑задачи

* `crontab.txt` хранится в **внешнем** репозитории, который тянет `git-sync`.
* Каждая строка: «5 полей расписания» + **абсолютная** команда.
* Пример строки:

  ```cron
  */2 * * * * /usr/local/bin/python -u /app/project/docker_test/app/scripts/hello.py
  ```
* Вывод задач идёт в STDOUT контейнера `app`:

  ```bash
  docker compose logs -f app
  ```
* При изменении `crontab.txt` хэш меняется → `app` перезапускает supercronic и начинает выполнять **новое** расписание без пересборки образа.

---

## Типовой поток обновлений (git‑pull)

1. Вы коммитите в внешний репозиторий: меняете код, `requirements.txt` и/или `crontab.txt`.
2. `git-sync` тянет коммит (смотрите `docker compose logs -f git-sync`).
3. `app` через ≤ `POLL_SEC`:

   * видит новый хэш `requirements.txt` → ставит/обновляет зависимости;
   * видит новый хэш `crontab.txt` → мягко перезапускает supercronic.
4. Новые задачи и зависимости начинают работать **без** пересборки образа.

---

## Команды админа (часто используемые)

* Состояние сервисов:

  ```bash
  docker compose ps
  ```
* Логи:

  ```bash
  docker compose logs -f git-sync
  docker compose logs -f app
  ```
* Шелл внутрь контейнера:

  ```bash
  docker compose exec app sh
  docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
  ```
* Проверка, что файлы и хэши видны:

  ```bash
  docker compose exec app sh -lc 'echo "$REQ_FILE"; sha256sum "$REQ_FILE"; cat /var/lib/app-state/requirements.sha256 || true'
  docker compose exec app sh -lc 'echo "$CRON_FILE"; sha256sum "$CRON_FILE"; cat /var/lib/app-state/crontab.sha256 || true'
  ```
* Полный сброс (ОСТОРОЖНО, удалит данные БД и локальные образы проекта):

  ```bash
  docker compose down -v --rmi local
  ```

---

## Частые проблемы и что делать

* **`fe_sendauth: no password supplied`**
  В `app` не проброшены креды БД. Задайте `DATABASE_URL` **или** `PG*` переменные в `environment` сервиса `app` и пересоздайте контейнер.

* **Не видно новых задач после изменения `crontab.txt`**
  Ждите ≤ `POLL_SEC`. Если изменилось — в логах `app` увидите событие «обнаружено изменение cron‑файла».

* **Зависимости не ставятся**
  Проверьте доступ к PyPI и путь `REQ_FILE`. Смотрите логи `app` — там будет «Устанавливаю зависимости…».

* **Read‑only ошибки при записи**
  Кодовый том смонтирован `:ro`. Нельзя писать в `/app/project/docker_test/...`. Все служебные файлы и хэши — только в `/var/lib/app-state`.

* **Предупреждение Compose про `version:`**
  Для Compose v2 поле `version` устарело и игнорируется. Можно удалить строку `version:` из `docker-compose.yml`.

---

## Лицензия

MIT

```
Этот проект распространяется под MIT License. Используйте, модифицируйте и адаптируйте под свои задачи.
```

Для тестирования работоспособности используются репозитории:

[1]: https://github.com/shurikovyy/pg_git_project_ready.git "GitHub - shurikovyy/pg_git_project_ready"
[2]: https://github.com/shurikovyy/docker_test "GitHub - shurikovyy/docker_test: Testing the ability to sync with GIT"
