# routes/gdpr.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash, render_template, make_response
from flask_login import login_required, current_user, logout_user
from models import db, Session
import json

# Create GDPR blueprint
gdpr_bp = Blueprint('gdpr', __name__)

# Export user data as downloadable JSON file
@gdpr_bp.route('/user/export', methods=['GET'])
@login_required
def export_user_data():
    user = current_user
    data = {
        'username': user.username,
        'email': user.email,
        'auctions_created': [a.title for a in user.auctions],
        'bids_made': [
            {'auction': b.auction.title, 'amount': b.bid_amount} for b in user.bids
        ]
    }
    response = make_response(json.dumps(data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename="user_data_export.json"'
    return response


# Delete user account and related data
@gdpr_bp.route('/user/delete', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        # 🔐 User confirmed deletion
        user = current_user

        # Delete user's bids and auctions first (ensure foreign keys are handled)
        for bid in user.bids:
            db.session.delete(bid)
        for auction in user.auctions:
            db.session.delete(auction)

        # Delete session records
        Session.query.filter_by(user_id=user.id).delete()

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        # Logout
        logout_user()
        flash("Your account and data have been permanently deleted.", "success")
        return redirect(url_for('home'))
    
    # 👀 Initial GET request: show confirmation page
    return render_template('confirm_delete.html')
