-- CreateTable
CREATE TABLE "Voter" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "idNumber" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "sex" TEXT NOT NULL,
    "age" INTEGER NOT NULL,
    "state" TEXT NOT NULL,
    "publicKeyRSA" TEXT NOT NULL,
    "privateKeyRSA" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "Vote" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "vote" TEXT NOT NULL,
    "sex" TEXT NOT NULL,
    "age" INTEGER NOT NULL,
    "state" TEXT NOT NULL,
    "signatureRSA" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Voter_idNumber_key" ON "Voter"("idNumber");
