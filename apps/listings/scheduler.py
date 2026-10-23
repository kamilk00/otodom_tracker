import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

logger = logging.getLogger(__name__)


def run_price_update():
    """Trigger the update_prices management command programmatically."""
    logger.info("APScheduler: Rozpoczynam automatyczne odświeżanie cen...")
    try:
        call_command('update_prices')
    except Exception as e:
        logger.error(f"APScheduler: Błąd podczas odświeżania cen: {e}")


def start_scheduler():
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_price_update, 
        'interval', 
        hours = 12, 
        id = 'otodom_price_updater', 
        replace_existing = True
    )
    
    scheduler.start()
    logger.info("APScheduler: Scheduler został pomyślnie uruchomiony w tle.")