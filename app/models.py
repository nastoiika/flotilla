from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Boat(db.Model):
    __tablename__ = "boats"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    boat_type = db.Column(db.String(100), nullable=False)
    displacement = db.Column(db.Float, nullable=False)
    build_date = db.Column(db.Date, nullable=False)

    trips = db.relationship("Trip", back_populates="boat", cascade="all, delete-orphan")


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    boat_id = db.Column(db.Integer, db.ForeignKey("boats.id"), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)

    boat = db.relationship("Boat", back_populates="trips")
    crew = db.relationship("CrewMember", back_populates="trip", cascade="all, delete-orphan")
    catches = db.relationship("FishCatch", back_populates="trip", cascade="all, delete-orphan")
    bank_visits = db.relationship("BankVisit", back_populates="trip", cascade="all, delete-orphan")

    @property
    def total_catch(self):
        return sum(c.weight for c in self.catches)


class CrewMember(db.Model):
    __tablename__ = "crew_members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)  # должность (капитан и т.д.)

    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    trip = db.relationship("Trip", back_populates="crew")


# --- СПРАВОЧНИК ВИДОВ РЫБ ---
class FishType(db.Model):
    __tablename__ = "fish_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # треска, окунь, хек и т.д.

    catches = db.relationship("FishCatch", back_populates="fish_type", cascade="all, delete-orphan")


class New_FishType(db.Model):
    __tablename__ = "fish_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class FishCatch(db.Model):
    __tablename__ = "fish_catches"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    fish_type_id = db.Column(db.Integer, db.ForeignKey("fish_types.id"), nullable=False)
    weight = db.Column(db.Float, nullable=False)

    trip = db.relationship("Trip", back_populates="catches")
    fish_type = db.relationship("FishType", back_populates="catches")


class BankVisit(db.Model):
    __tablename__ = "bank_visits"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)

    bank_name = db.Column(db.String(100), nullable=False)
    arrival_date = db.Column(db.Date, nullable=False)
    departure_date = db.Column(db.Date, nullable=False)

    fish_quality = db.Column(db.String(20), nullable=False)  # отличное/хорошее/плохое

    trip = db.relationship("Trip", back_populates="bank_visits")
