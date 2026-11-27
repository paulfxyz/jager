# syntax=docker/dockerfile:1
# Small, boring, non-root. Boring is the goal.
FROM python:3.12-slim AS build
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim
# A user with no shell and no home: if someone gets in, there is nothing to look at.
RUN useradd --system --no-create-home --shell /usr/sbin/nologin jager && mkdir /data && chown jager /data
COPY --from=build /install /usr/local
ENV JAGER_HOST=0.0.0.0 JAGER_DB=/data/jager.db PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER jager
VOLUME /data
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/health', timeout=4)" || exit 1
CMD ["jager", "serve"]
