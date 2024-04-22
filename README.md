### Postgres docker instance

```
docker run \
-e POSTGRES_USER=allnighter_db \
-e POSTGRES_PASSWORD=supersecretpassword \
-e POSTGRES_DB=allnighter_db \
-v allnighterdata:/var/lib/postgresql/data \
--name allnighter_db \
--rm \
-p 7654:5432 \
--network allnighternetwork \
postgres:16
```
