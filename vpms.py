from app import app, db
from app.models import User, ParkingSlot, ParkingPrice, ParkingHistory


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'ParkingSlot':ParkingSlot, 'ParkingHistory':ParkingHistory, 'ParkingPrice':ParkingPrice}

if __name__ == "__main__":
    app.run(debug=True)