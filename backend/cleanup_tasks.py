from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from backend.models import User, Category, Product, ProductCategory, db
import logging

logger = logging.getLogger(__name__)


def cleanup_inactive_accounts():
    try:
        one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)

        never_logged_users = User.query.filter(
            User.last_login.is_(None),
            User.created_at < one_month_ago
        ).all()
        
        inactive_users = User.query.filter(
            User.last_login.isnot(None),
            User.last_login < one_month_ago
        ).all()
        
        all_inactive_users = never_logged_users + inactive_users
        
        deleted_count = 0
        for user in all_inactive_users:
            logger.info(f"Eliminando cuenta inactiva: {user.username} (ID: {user.id})")
            
            db.session.delete(user)
            deleted_count += 1
        
        if deleted_count > 0:
            db.session.commit()
            logger.info(f"✅ Limpieza completada: {deleted_count} cuentas inactivas eliminadas")
        else:
            logger.info("✅ No hay cuentas inactivas para eliminar")
            
        return deleted_count
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en limpieza de cuentas: {str(e)}")
        return 0


def cleanup_unused_categories():
    try:
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        unused_categories = db.session.query(Category).filter(
            Category.is_default == False,
            Category.owner_id.isnot(None),
            ~Category.id.in_(
                db.session.query(ProductCategory.category_id).filter(
                    ProductCategory.created_at >= one_week_ago
                ).subquery()
            ),
            Category.created_at < one_week_ago
        ).all()
        
        deleted_count = 0
        for category in unused_categories:
            product_count = db.session.query(ProductCategory).filter_by(
                category_id=category.id
            ).count()
            
            if product_count == 0:
                logger.info(f"Eliminando categoría no utilizada: {category.name} (ID: {category.id})")
                db.session.delete(category)
                deleted_count += 1
            else:
                logger.debug(f"Manteniendo categoría con productos: {category.name} ({product_count} productos)")
        
        if deleted_count > 0:
            db.session.commit()
            logger.info(f"✅ Limpieza completada: {deleted_count} categorías no utilizadas eliminadas")
        else:
            logger.info("✅ No hay categorías no utilizadas para eliminar")
            
        return deleted_count
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error en limpieza de categorías: {str(e)}")
        return 0


def run_full_cleanup():

    logger.info(" Iniciando limpieza automática del sistema...")
    
    deleted_accounts = cleanup_inactive_accounts()
    
    deleted_categories = cleanup_unused_categories()
    
    logger.info(f"Limpieza completada - Cuentas eliminadas: {deleted_accounts}, Categorías eliminadas: {deleted_categories}")
    
    return {
        'deleted_accounts': deleted_accounts,
        'deleted_categories': deleted_categories,
        'timestamp': datetime.now(timezone.utc)
    }


def get_cleanup_stats():
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    never_logged_count = User.query.filter(
        User.last_login.is_(None),
        User.created_at < one_month_ago
    ).count()
    
    inactive_count = User.query.filter(
        User.last_login.isnot(None),
        User.last_login < one_month_ago
    ).count()
    
    unused_categories_count = db.session.query(Category).filter(
        Category.is_default == False,
        Category.owner_id.isnot(None),
        ~Category.id.in_(
            db.session.query(ProductCategory.category_id).filter(
                ProductCategory.created_at >= one_week_ago
            ).subquery()
        ),
        Category.created_at < one_week_ago
    ).count()
    
    return {
        'inactive_accounts': never_logged_count + inactive_count,
        'unused_categories': unused_categories_count,
        'last_check': datetime.now(timezone.utc)
    }
