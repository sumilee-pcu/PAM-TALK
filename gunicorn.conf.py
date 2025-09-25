# Gunicorn 설정 파일
# PAM-TALK API 서버 최적화용

import multiprocessing

# 서버 소켓
bind = "0.0.0.0:5000"
backlog = 2048

# 워커 설정
workers = multiprocessing.cpu_count() * 2 + 1  # CPU 코어 * 2 + 1
worker_class = "gevent"  # 비동기 워커
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 타임아웃 설정
timeout = 30
keepalive = 2

# 로깅
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" in %(D)sμs'

# 프로세스 관리
user = None
group = None
tmp_upload_dir = None
pidfile = "gunicorn.pid"

# SSL (필요시)
keyfile = None
certfile = None

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)