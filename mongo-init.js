let ROOT_USERNAME = process.env.MONGO_INITDB_ROOT_USERNAME;
let ROOT_PASSWORD = process.env.MONGO_INITDB_ROOT_PASSWORD;

print(
  db.createUser({
    user: ROOT_USERNAME,
    pwd: ROOT_PASSWORD,
    roles: [
      { role: "userAdminAnyDatabase", db: "admin" },
      "userAdminAnyDatabase",
    ],
  })
);
