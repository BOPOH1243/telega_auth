from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sessions.models import Session
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Запуск Telegram-бота'

    def handle(self, *args, **kwargs):
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            session_key = context.args[0] if context.args else None
            if session_key:
                telegram_id = update.message.from_user.id
                telegram_username = update.message.from_user.username

                # Обернутый вызов синхронного кода
                user, created = await sync_to_async(CustomUser.objects.get_or_create)(
                    telegram_id=telegram_id,
                    defaults={'username': telegram_username}
                )

                if not created and not user.telegram_username:
                    user.telegram_username = telegram_username
                    await sync_to_async(user.save)()

                try:
                    session = await sync_to_async(Session.objects.get)(session_key=session_key)
                    session_data = session.get_decoded()
                    session_data['_auth_user_id'] = user.id
                    session_data['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
                    session_data['_auth_user_hash'] = user.get_session_auth_hash()
                    session.session_data = Session.objects.encode(session_data)
                    await sync_to_async(session.save)()

                    await update.message.reply_text(f'Пользователь {user.username} успешно авторизован.')
                except Session.DoesNotExist:
                    await update.message.reply_text('Сессия не найдена.')
            else:
                await update.message.reply_text('Не указан идентификатор сессии.')

        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)

        application.run_polling()
