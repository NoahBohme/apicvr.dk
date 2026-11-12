import sqlite3
import os
import threading
import time
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
from urllib.parse import urlsplit

DB_PATH = os.getenv("STATS_DB_PATH", "stats.db")

# Our own host shows up as the referer on internal navigation; hide it from
# the "calling domains" list so external callers aren't drowned out.
_OWN_HOSTS = {
    h for h in (urlsplit(os.getenv("SITE_URL", "https://apicvr.dk")).hostname or "",)
    if h
}
_OWN_HOSTS |= {f"www.{h}" for h in _OWN_HOSTS if not h.startswith("www.")}

_PUBLIC_STATS_TTL = 600  # seconds
_public_stats_cache = {"at": 0.0, "data": None}
_public_stats_lock = threading.Lock()


def init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS request_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                status_code INTEGER,
                response_time_ms REAL,
                ip TEXT,
                referer TEXT
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON request_log(timestamp)"
        )
        # Migrate existing DBs that lack the new columns
        for col, coltype in [("ip", "TEXT"), ("referer", "TEXT")]:
            try:
                conn.execute(f"ALTER TABLE request_log ADD COLUMN {col} {coltype}")
            except sqlite3.OperationalError:
                pass
        # Calling domain per request (from Referer, else Origin), so the
        # dashboard can list one domain's requests via an index.
        try:
            conn.execute("ALTER TABLE request_log ADD COLUMN domain TEXT")
        except sqlite3.OperationalError:
            pass
        else:
            # One-off: derive it for historical rows from the stored referer.
            conn.create_function("domain_of", 1, _domain_of, deterministic=True)
            conn.execute(
                "UPDATE request_log SET domain = domain_of(referer) WHERE referer IS NOT NULL"
            )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_domain_timestamp ON request_log(domain, timestamp)"
        )
        # Running per-domain totals, kept up to date by log_request so the
        # dashboard never has to scan request_log to answer "who calls us".
        conn.execute("""
            CREATE TABLE IF NOT EXISTS caller_domains (
                domain TEXT PRIMARY KEY,
                count INTEGER NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)
        if conn.execute("SELECT 1 FROM caller_domains LIMIT 1").fetchone() is None:
            conn.execute(
                """
                INSERT INTO caller_domains (domain, count, first_seen, last_seen)
                SELECT domain, COUNT(*), MIN(timestamp), MAX(timestamp)
                FROM request_log WHERE domain IS NOT NULL GROUP BY domain
                """
            )


def _domain_of(url):
    """Hostname from a Referer/Origin header value, or None."""
    if not url:
        return None
    try:
        host = urlsplit(url if "//" in url else f"//{url}").hostname
    except ValueError:
        return None
    return host or None


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def log_request(method: str, path: str, status_code: int, response_time_ms: float, ip: str = None, referer: str = None, origin: str = None):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    # Browsers with a strict referrer policy omit Referer on cross-origin
    # fetches but still send Origin, so fall back to it for the domain.
    domain = _domain_of(referer) or _domain_of(origin)
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO request_log (timestamp, method, path, status_code, response_time_ms, ip, referer, domain) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ts, method, path, status_code, round(response_time_ms, 2), ip, referer or None, domain),
        )
        if domain:
            conn.execute(
                """
                INSERT INTO caller_domains (domain, count, first_seen, last_seen) VALUES (?, 1, ?, ?)
                ON CONFLICT(domain) DO UPDATE SET count = count + 1, last_seen = excluded.last_seen
                """,
                (domain, ts, ts),
            )


def get_stats() -> dict:
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    this_month = now.strftime("%Y-%m")
    if now.month == 1:
        last_month = f"{now.year - 1}-12"
    else:
        last_month = f"{now.year}-{now.month - 1:02d}"
    if now.month == 12:
        next_month = f"{now.year + 1}-01"
    else:
        next_month = f"{now.year}-{now.month + 1:02d}"
    # Plain range bounds so the WHERE clauses can use idx_timestamp;
    # wrapping the column in date()/strftime() forces a full table scan.
    month_start = f"{this_month}-01"
    next_month_start = f"{next_month}-01"
    last_month_start = f"{last_month}-01"

    with _get_conn() as conn:

        def count(where, params=()):
            return conn.execute(
                f"SELECT COUNT(*) FROM request_log WHERE {where}", params
            ).fetchone()[0]

        today_count = count("timestamp >= ? AND timestamp < ?", (today, tomorrow))
        week_count = count("timestamp >= ?", (week_start,))
        this_month_count = count("timestamp >= ? AND timestamp < ?", (month_start, next_month_start))
        last_month_count = count("timestamp >= ? AND timestamp < ?", (last_month_start, month_start))

        avg_response = conn.execute(
            "SELECT AVG(response_time_ms) FROM request_log WHERE timestamp >= ? AND timestamp < ?",
            (today, tomorrow),
        ).fetchone()[0]

        top_endpoints_today = conn.execute(
            """
            SELECT path, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY path ORDER BY count DESC LIMIT 15
            """,
            (today, tomorrow),
        ).fetchall()

        top_endpoints_week = conn.execute(
            """
            SELECT path, COUNT(*) as count FROM request_log
            WHERE timestamp >= ?
            GROUP BY path ORDER BY count DESC LIMIT 15
            """,
            (week_start,),
        ).fetchall()

        top_endpoints_month = conn.execute(
            """
            SELECT path, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY path ORDER BY count DESC LIMIT 15
            """,
            (month_start, next_month_start),
        ).fetchall()

        hourly_today = conn.execute(
            """
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM request_log WHERE timestamp >= ? AND timestamp < ?
            GROUP BY hour ORDER BY hour
            """,
            (today, tomorrow),
        ).fetchall()

        daily_week = conn.execute(
            """
            SELECT date(timestamp) as day, COUNT(*) as count
            FROM request_log WHERE timestamp >= ?
            GROUP BY day ORDER BY day
            """,
            (week_start,),
        ).fetchall()

        daily_month = conn.execute(
            """
            SELECT date(timestamp) as day, COUNT(*) as count
            FROM request_log WHERE timestamp >= ? AND timestamp < ?
            GROUP BY day ORDER BY day
            """,
            (month_start, next_month_start),
        ).fetchall()

        top_ips_today = conn.execute(
            """
            SELECT ip, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND timestamp < ? AND ip IS NOT NULL
            GROUP BY ip ORDER BY count DESC LIMIT 15
            """,
            (today, tomorrow),
        ).fetchall()

        top_ips_week = conn.execute(
            """
            SELECT ip, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND ip IS NOT NULL
            GROUP BY ip ORDER BY count DESC LIMIT 15
            """,
            (week_start,),
        ).fetchall()

        top_ips_month = conn.execute(
            """
            SELECT ip, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND timestamp < ? AND ip IS NOT NULL
            GROUP BY ip ORDER BY count DESC LIMIT 15
            """,
            (month_start, next_month_start),
        ).fetchall()

        top_referers_today = conn.execute(
            """
            SELECT referer, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND timestamp < ? AND referer IS NOT NULL
            GROUP BY referer ORDER BY count DESC LIMIT 15
            """,
            (today, tomorrow),
        ).fetchall()

        top_referers_week = conn.execute(
            """
            SELECT referer, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND referer IS NOT NULL
            GROUP BY referer ORDER BY count DESC LIMIT 15
            """,
            (week_start,),
        ).fetchall()

        top_referers_month = conn.execute(
            """
            SELECT referer, COUNT(*) as count FROM request_log
            WHERE timestamp >= ? AND timestamp < ? AND referer IS NOT NULL
            GROUP BY referer ORDER BY count DESC LIMIT 15
            """,
            (month_start, next_month_start),
        ).fetchall()

        own = sorted(_OWN_HOSTS)
        caller_domains = conn.execute(
            f"""
            SELECT domain, count, first_seen, last_seen FROM caller_domains
            WHERE domain NOT IN ({",".join("?" * len(own))})
            ORDER BY last_seen DESC LIMIT 2000
            """,
            own,
        ).fetchall()

        return {
            "today": today_count,
            "week": week_count,
            "this_month": this_month_count,
            "last_month": last_month_count,
            "avg_response_ms": round(avg_response or 0, 1),
            "today_label": now.strftime("%d. %b %Y"),
            "week_label": f"Fra {week_start}",
            "this_month_label": now.strftime("%B %Y"),
            "last_month_label": last_month,
            "top_endpoints_today": [
                {"path": r["path"], "count": r["count"]} for r in top_endpoints_today
            ],
            "top_endpoints_week": [
                {"path": r["path"], "count": r["count"]} for r in top_endpoints_week
            ],
            "top_endpoints_month": [
                {"path": r["path"], "count": r["count"]} for r in top_endpoints_month
            ],
            "hourly_today": [
                {"hour": r["hour"], "count": r["count"]} for r in hourly_today
            ],
            "daily_week": [
                {"day": r["day"], "count": r["count"]} for r in daily_week
            ],
            "daily_month": [
                {"day": r["day"], "count": r["count"]} for r in daily_month
            ],
            "top_ips_today": [{"ip": r["ip"], "count": r["count"]} for r in top_ips_today],
            "top_ips_week": [{"ip": r["ip"], "count": r["count"]} for r in top_ips_week],
            "top_ips_month": [{"ip": r["ip"], "count": r["count"]} for r in top_ips_month],
            "top_referers_today": [{"referer": r["referer"], "count": r["count"]} for r in top_referers_today],
            "top_referers_week": [{"referer": r["referer"], "count": r["count"]} for r in top_referers_week],
            "top_referers_month": [{"referer": r["referer"], "count": r["count"]} for r in top_referers_month],
            "caller_domains": [dict(r) for r in caller_domains],
        }


def get_domain_requests(domain: str, limit: int = 500) -> dict:
    """Latest requests from one calling domain, plus a per-IP breakdown."""
    with _get_conn() as conn:
        requests = conn.execute(
            """
            SELECT timestamp, method, path, status_code, response_time_ms, ip, referer
            FROM request_log WHERE domain = ?
            ORDER BY timestamp DESC LIMIT ?
            """,
            (domain, limit),
        ).fetchall()
        ips = conn.execute(
            """
            SELECT ip, COUNT(*) AS count, MAX(timestamp) AS last_seen
            FROM request_log WHERE domain = ?
            GROUP BY ip ORDER BY count DESC LIMIT 100
            """,
            (domain,),
        ).fetchall()
    return {
        "domain": domain,
        "requests": [dict(r) for r in requests],
        "ips": [dict(r) for r in ips],
    }


def get_public_stats():
    """Aggregate counters safe to show on the public homepage.

    Cached for _PUBLIC_STATS_TTL seconds and limited to index-only lookups,
    so it's cheap even on a multi-GB request_log. Returns None if the stats
    DB is unavailable; callers should hide the stats section in that case.
    """
    cache = _public_stats_cache
    if cache["data"] is not None and time.monotonic() - cache["at"] < _PUBLIC_STATS_TTL:
        return cache["data"]
    # Only one thread refreshes; the others serve the stale value meanwhile.
    if not _public_stats_lock.acquire(blocking=cache["data"] is None):
        return cache["data"]
    try:
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        with _get_conn() as conn:
            # Separate queries: SQLite only applies its min/max index shortcut
            # when the aggregate stands alone.
            total = conn.execute("SELECT MAX(id) FROM request_log").fetchone()[0]
            first_ts = conn.execute("SELECT MIN(timestamp) FROM request_log").fetchone()[0]
            last_30d = conn.execute(
                "SELECT COUNT(*) FROM request_log WHERE timestamp >= ?", (month_ago,)
            ).fetchone()[0]
            today_count = conn.execute(
                "SELECT COUNT(*) FROM request_log WHERE timestamp >= ?", (today,)
            ).fetchone()[0]
        cache["data"] = {
            "total": total or 0,
            "since": first_ts[:10] if first_ts else None,
            "last_30d": last_30d,
            "per_day": round(last_30d / 30),
            "today": today_count,
        }
        cache["at"] = time.monotonic()
    except sqlite3.Error:
        pass
    finally:
        _public_stats_lock.release()
    return cache["data"]
