from flask import Flask, render_template, request, redirect, url_for
from models import db, Boat, CrewMember, FishCatch, FishType, Trip, BankVisit
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:790011@localhost:5432/postgres'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def index():
    return render_template("index.html")

# ----------- СПИСОК КАТЕРОВ -----------
@app.route("/boats")
def boats_list():
    boats = Boat.query.all()
    return render_template("boats_list.html", boats=boats)

# ----------- ДОБАВЛЕНИЕ КАТЕРА -----------
@app.route("/boats/add", methods=["GET", "POST"])
def add_boat():
    if request.method == "POST":
        name = request.form["name"]
        boat_type = request.form["boat_type"]
        displacement = float(request.form["displacement"])
        build_date = datetime.strptime(request.form["build_date"], "%Y-%m-%d")

        new_boat = Boat(
            name=name,
            boat_type=boat_type,
            displacement=displacement,
            build_date=build_date
        )
        db.session.add(new_boat)
        db.session.commit()

        return redirect(url_for("boats_list"))

    return render_template("boat_form.html", boat=None)

@app.route("/boats/<int:boat_id>/edit", methods=["GET", "POST"])
def edit_boat(boat_id):
    boat = Boat.query.get_or_404(boat_id)

    if request.method == "POST":
        boat.name = request.form["name"]
        boat.boat_type = request.form["boat_type"]
        boat.displacement = float(request.form["displacement"])
        boat.build_date = datetime.strptime(request.form["build_date"], "%Y-%m-%d")

        db.session.commit()
        return redirect(url_for("boats_list"))

    return render_template("boat_form.html", boat=boat)


# --- Список рейсов ---
@app.route("/trips")
def trips_list():
    trips = Trip.query.order_by(Trip.departure_date.desc()).all()
    return render_template("trips_list.html", trips=trips)


# --- Добавление рейса ---
@app.route("/trips/add", methods=["GET", "POST"])
def add_trip():
    boats = Boat.query.all()

    if request.method == "POST":
        boat_id = int(request.form["boat_id"])
        departure_date = datetime.strptime(request.form["departure_date"], "%Y-%m-%d")
        return_date_str = request.form.get("return_date")
        return_date = datetime.strptime(return_date_str, "%Y-%m-%d") if return_date_str else None

        new_trip = Trip(boat_id=boat_id, departure_date=departure_date, return_date=return_date)
        db.session.add(new_trip)
        db.session.commit()

        # --- Добавление команды ---
        names = request.form.getlist("crew_name")
        positions = request.form.getlist("crew_position")

        for name, position in zip(names, positions):
            if name.strip() == "":
                continue
            member = CrewMember(name=name, position=position, trip_id=new_trip.id)
            db.session.add(member)

        db.session.commit()
        return redirect(url_for("trips_list"))

    return render_template("trip_form.html", boats=boats)

@app.route("/banks")
def banks_list():
    # Получаем все уникальные банки
    banks = db.session.query(BankVisit.bank_name).distinct().all()
    banks_data = []

    for (bank_name,) in banks:
        # Все посещения этой банки
        visits = BankVisit.query.filter_by(bank_name=bank_name).all()

        # Если нет улова, пропускаем
        catches_per_trip = []
        for visit in visits:
            trip_catch = sum(c.weight for c in visit.trip.catches)
            catches_per_trip.append((visit.trip.boat, trip_catch))

        if catches_per_trip:
            avg_catch = sum(catch for _, catch in catches_per_trip) / len(catches_per_trip)
            boats_above_avg = [boat.name for boat, catch in catches_per_trip if catch > avg_catch]
        else:
            boats_above_avg = []

        banks_data.append({
            "bank_name": bank_name,
            "boats_above_avg": boats_above_avg,
        })

    return render_template("banks_list.html", banks_data=banks_data)

@app.route("/trips/<int:trip_id>/add_bank", methods=["GET", "POST"])
def add_bank(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    if request.method == "POST":
        bank_name = request.form["bank_name"]
        arrival_date = datetime.strptime(request.form["arrival_date"], "%Y-%m-%d")
        departure_date = datetime.strptime(request.form["departure_date"], "%Y-%m-%d")
        fish_quality = request.form["fish_quality"]

        bank = BankVisit(
            trip_id=trip.id,
            bank_name=bank_name,
            arrival_date=arrival_date,
            departure_date=departure_date,
            fish_quality=fish_quality
        )
        db.session.add(bank)
        db.session.commit()

        return redirect(url_for("trips_list"))

    return render_template("bank_form.html", trip=trip)

@app.route("/banks/<int:bank_id>/add_catch", methods=["GET", "POST"])
def add_catch(bank_id):
    bank = BankVisit.query.get_or_404(bank_id)
    trip = bank.trip
    fish_types = FishType.query.all()

    if request.method == "POST":
        fish_type_id = int(request.form["fish_type_id"])
        weight = float(request.form["weight"])

        catch = FishCatch(
            trip_id=trip.id,
            fish_type_id=fish_type_id,
            weight=weight
        )
        db.session.add(catch)
        db.session.commit()

        return redirect(url_for("banks_list"))

    return render_template("catch_form.html", bank=bank, trip=trip, fish_types=fish_types)

@app.route("/catch_report", methods=["GET", "POST"])
def catch_report():
    fish_types = FishType.query.all()
    banks = db.session.query(BankVisit.bank_name).distinct().all()
    report = []

    selected_fish_type_id = None
    selected_bank_name = None

    if request.method == "POST":
        selected_fish_type_id = int(request.form["fish_type_id"])
        selected_bank_name = request.form["bank_name"]

        # все банки с таким именем
        bank_visits = BankVisit.query.filter_by(bank_name=selected_bank_name).all()

        for visit in bank_visits:
            # ищем улов данного сорта для рейса
            catch = FishCatch.query.filter_by(
                trip_id=visit.trip_id,
                fish_type_id=selected_fish_type_id
            ).first()
            if catch:
                report.append({
                    "trip": visit.trip,
                    "weight": catch.weight,
                    "arrival_date": visit.arrival_date,
                    "departure_date": visit.departure_date
                })

    return render_template(
        "catch_report.html",
        fish_types=fish_types,
        banks=banks,
        report=report,
        selected_fish_type_id=selected_fish_type_id,
        selected_bank_name=selected_bank_name
    )

@app.route("/report/fish_max_catch", methods=["GET", "POST"])
def fish_max_catch():
    fish_types = FishType.query.all()
    result = []
    start_date = None
    end_date = None

    if request.method == "POST":
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")

        for fish in fish_types:
            # все уловы выбранного сорта в интервале дат рейсов
            catches = FishCatch.query.join(Trip).filter(
                FishCatch.fish_type_id == fish.id,
                Trip.departure_date >= start_date,
                Trip.departure_date <= end_date
            ).all()

            if catches:
                # находим максимальный улов
                max_weight = max(c.weight for c in catches)
                boats = [c.trip.boat.name for c in catches if c.weight == max_weight]
            else:
                max_weight = None
                boats = []

            result.append({
                "fish_name": fish.name,
                "max_weight": max_weight,
                "boats": boats
            })

    return render_template(
        "fish_max_catch.html",
        fish_types=fish_types,
        result=result,
        start_date=start_date,
        end_date=end_date
    )

@app.route("/report/bank_avg_catch", methods=["GET", "POST"])
def bank_avg_catch():
    banks = db.session.query(BankVisit.bank_name).distinct().all()
    report = []
    start_date = None
    end_date = None

    if request.method == "POST":
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")

        for (bank_name,) in banks:
            visits = BankVisit.query.join(Trip).filter(
                BankVisit.bank_name == bank_name,
                Trip.departure_date >= start_date,
                Trip.departure_date <= end_date
            ).all()

            total_weight = 0
            count = 0
            for visit in visits:
                for c in visit.trip.catches:
                    total_weight += c.weight
                    count += 1

            avg_weight = (total_weight / count) if count else None

            report.append({
                "bank_name": bank_name,
                "avg_weight": avg_weight
            })

    return render_template(
        "bank_avg_catch.html",
        report=report,
        start_date=start_date,
        end_date=end_date
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
