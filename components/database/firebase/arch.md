### firebase (database)

Firebase (Firestore + Auth) owns persistence and identity. All reads and writes
go through a thin data-access layer — application code never calls the Firebase
SDK directly from screens or route handlers, so the backend can be emulated in
tests and swapped later. Model collections and document shapes in one schema
module; ad-hoc document structures are how Firestore data rots.
