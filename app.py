import os
import calendar
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from typing import List
from errors import init_error_handlers

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    init_error_handlers(app)

    # Database configuration
    db_path = os.path.join(os.path.dirname(__file__), 'db', 'data.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure the 'db' directory exists
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        if not os.path.exists(db_path):
            db.create_all()
            print(f"Database created at {db_path}")

    return app

# Initialize database
db = SQLAlchemy()

class ChainDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    chain_name = db.Column(db.String(50), nullable=False)

class Chain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_chains', methods=['GET'])
def get_chains():
    """Retrieve all chains."""
    chains = [chain.name for chain in Chain.query.all()]
    return jsonify(chains)

@app.route('/add_chain', methods=['POST'])
def add_chain():
    """Add a new chain."""
    chain_name = request.json.get('chain_name')
    if not chain_name:
        return jsonify({"error": "No chain name provided"}), 400
    if Chain.query.filter_by(name=chain_name).first():
        return jsonify({"error": "Chain already exists"}), 400

    new_chain = Chain(name=chain_name)
    db.session.add(new_chain)
    db.session.commit()
    return jsonify({"message": "Chain added successfully"}), 201

@app.route('/delete_chain', methods=['POST'])
def delete_chain():
    """Delete a chain and its associated dates."""
    chain_name = request.json.get('chain_name')
    if not chain_name:
        return jsonify({"error": "No chain name provided"}), 400

    chain = Chain.query.filter_by(name=chain_name).first()
    if not chain:
        return jsonify({"error": "Chain not found"}), 404

    # Delete associated dates
    ChainDate.query.filter_by(chain_name=chain_name).delete()
    db.session.delete(chain)
    db.session.commit()
    return jsonify({"message": "Chain deleted successfully"}), 200

@app.route('/mark_date', methods=['POST'])
def mark_date():
    """Mark or unmark a date for a specific chain."""
    date = request.json.get('date')
    chain_name = request.json.get('chain_name')
    if not date or not chain_name:
        return jsonify({"error": "Date or chain name not provided"}), 400

    existing_date = ChainDate.query.filter_by(date=date, chain_name=chain_name).first()

    if not existing_date:
        # Mark the date
        new_date = ChainDate(date=date, chain_name=chain_name)
        db.session.add(new_date)
        db.session.commit()
        return jsonify({"message": "marked"}), 200

    # Unmark the date
    db.session.delete(existing_date)
    db.session.commit()
    return jsonify({"message": "unmarked"}), 200

@app.route('/get_dates', methods=['GET'])
def get_dates() -> List[str]:
    """Retrieve all marked dates for a specific chain."""
    chain_name = request.args.get('chain_name')
    if not chain_name:
        return jsonify({"error": "No chain name provided"}), 400

    dates = [chain_date.date for chain_date in ChainDate.query.filter_by(chain_name=chain_name).all()]
    return jsonify(dates)

@app.route('/get_calendar', methods=['GET'])
def get_calendar():
    """Retrieve the calendar structure for the requested month and year."""
    year = request.args.get('year', default=datetime.today().year, type=int)
    month = request.args.get('month', default=datetime.today().month, type=int)

    # Generate the full month's calendar grid with padding days
    cal = calendar.Calendar(firstweekday=6)  # Start with Sunday
    month_days = cal.monthdays2calendar(year, month)  # [(day, weekday), ...]

    # Build a full calendar grid
    calendar_grid = []
    for week in month_days:
        for day, weekday in week:
            # day == 0 means a padding day (from previous/next month)
            calendar_grid.append({"day": day if day != 0 else None, "weekday": weekday})

    return jsonify({"year": year, "month": month, "days": calendar_grid})

@app.route('/manage_chains')
def manage_chains():
    """Render a page for managing chains."""
    return render_template('manage_chains.html')

@app.route('/chain_stats', methods=['GET'])
def chain_stats():
    """Get statistics for a specific chain."""
    chain_name = request.args.get('chain_name')
    if not chain_name:
        return jsonify({"error": "No chain name provided"}), 400

    # Retrieve all dates for the chain
    try:
        chain_dates = sorted(
            [datetime.strptime(cd.date, "%Y-%m-%d") for cd in ChainDate.query.filter_by(chain_name=chain_name).all()]
        )
    except Exception as e:
        print(f"Error parsing dates for chain '{chain_name}': {e}")
        return jsonify({"error": "Error processing chain data"}), 500

    if not chain_dates:
        # No marked dates for the chain
        return jsonify({
            "chain_name": chain_name,
            "current_streak": 0,
            "longest_streak": 0,
            "percent_marked": 0.0
        })

    # Calculate the statistics
    try:
        current_streak, longest_streak = 0, 0
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)
        previous_date = None
        temp_streak = 0

        for date in chain_dates:
            # Continue streak if dates are consecutive
            if previous_date and (date - previous_date).days == 1:
                temp_streak += 1
            else:
                # Save the longest streak found so far
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1  # Start a new streak

            # Update current streak if it extends to yesterday or today
            if date.date() in [yesterday, today]:
                current_streak = temp_streak

            previous_date = date

        # Final check for the longest streak
        longest_streak = max(longest_streak, temp_streak)

        # Calculate percentage of marked days in the current year
        start_of_year = datetime(today.year, 1, 1).date()
        total_days = (today - start_of_year).days + 1
        marked_days = len([d for d in chain_dates if d.date() >= start_of_year])
        percent_marked = (marked_days / total_days) * 100 if total_days > 0 else 0.0

        return jsonify({
            "chain_name": chain_name,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "percent_marked": round(percent_marked, 2)
        })

    except Exception as e:
        print(f"Error calculating stats for chain '{chain_name}': {e}")
        return jsonify({"error": "Error calculating chain statistics"}), 500

@app.route('/view_stats')
def view_stats():
    """Render the chain statistics page."""
    return render_template('chain_stats.html')

if __name__ == '__main__':
    app.run(debug=True)
