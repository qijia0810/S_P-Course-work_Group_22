from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, Auction, Bid, User
import logging


bidding_bp = Blueprint('bidding', __name__)


@bidding_bp.route('/auctions/')
@login_required
def list_auctions():
    active_auctions = Auction.query.filter_by(status='active').all()
    closed_auctions = Auction.query.filter_by(status='closed').all()

    return render_template('auctions.html',
                           active_auctions=active_auctions,
                           closed_auctions=closed_auctions,
                           datetime=datetime)


@bidding_bp.route('/auction/<int:auction_id>')
@login_required
def auction_detail(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.bid_amount.desc()).all()

    return render_template('auction_detail.html',
                           auction=auction,
                           bids=bids)


@bidding_bp.route('/auction/create', methods=['GET', 'POST'])
@login_required
def create_auction():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_price = float(request.form['start_price'])

        try:
            duration_days = int(request.form['duration'])
            if duration_days < 1:
                flash('Duration must be at least 1 day', 'error')
                return redirect(url_for('bidding.create_auction'))
        except ValueError:
            flash('Invalid duration value', 'error')
            return redirect(url_for('bidding.create_auction'))

        new_auction = Auction(
            title=title,
            description=description,
            start_price=start_price,
            current_price=start_price,
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(days=duration_days),
            status='active'
        )

        db.session.add(new_auction)
        db.session.commit()

        flash('Auction created successfully!', 'success')
        return redirect(url_for('bidding.list_auctions'))

    return render_template('create_auction.html')


@bidding_bp.route('/auction/<int:auction_id>/bid', methods=['POST'])
@login_required
def place_bid(auction_id):
    auction = Auction.query.get_or_404(auction_id)

    if auction.status == 'closed':
        flash('This auction has ended', 'error')
        return redirect(url_for('bidding.auction_detail', auction_id=auction_id))

    if current_user.id == auction.owner_id:
        flash('You cannot bid on your own auction', 'error')
        return redirect(url_for('bidding.auction_detail', auction_id=auction_id))

    try:
        bid_amount = float(request.form['bid_amount'])
    except ValueError:
        flash('Invalid bid amount', 'error')
        return redirect(url_for('bidding.auction_detail', auction_id=auction_id))

    if bid_amount <= auction.current_price:
        flash('Your bid must be higher than the current price', 'error')
        return redirect(url_for('bidding.auction_detail', auction_id=auction_id))

    new_bid = Bid(
        auction_id=auction_id,
        user_id=current_user.id,
        bid_amount=bid_amount
    )

    auction.current_price = bid_amount

    db.session.add(new_bid)
    db.session.commit()

    flash('Your bid has been placed!', 'success')
    return redirect(url_for('bidding.auction_detail', auction_id=auction_id))


@bidding_bp.route('/auction/<int:auction_id>/close', methods=['POST'])
@login_required
def close_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)

    if auction.owner_id != current_user.id:
        flash('You can only close your own auctions', 'error')
        return redirect(url_for('bidding.auction_detail', auction_id=auction_id))

    auction.status = 'closed'
    db.session.commit()

    flash('Auction closed successfully', 'success')
    return redirect(url_for('bidding.auction_detail', auction_id=auction_id))