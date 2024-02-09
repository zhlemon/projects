import os
import logging
import telegram
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '_token_key_'
API = '_api_key_'
# Set up Telegram bot
bot = telegram.Bot(TOKEN)
# Set up YouTube API client
youtube = build('youtube', 'v3', developerKey=API)
def playlist(playlist_id, youtube):
    video_response = youtube.playlistItems().list(
        playlistId=playlist_id,
        part='id,snippet',
        maxResults=10
    ).execute()
    video_links = []
    for result in video_response.get('items', []):
        video_id = result['snippet']['resourceId']['videoId']
        video_title = result['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append({'url': video_url, 'title': video_title})
    return video_links
def start(update, context):
    #Send a message when the command /start is issued.
    update.message.reply_text('Hi! Please enter the keywords to /search for YouTube playlists. \n'
                              'Use /help command for explanation how to find playlists')

def search(update, context):
    logging.info(f"Received update: {update}")
    #Search for YouTube playlists based on user input.
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Please enter a valid search query.')
        return
    search_response = youtube.search().list(
        q=query,
        type='playlist',
        part='id,snippet',
        maxResults=5
    ).execute()
    playlists = []
    for result in search_response.get('items', []):
        playlist_id = result['id']['playlistId']
        playlist_title = result['snippet']['title']
        playlists.append({'id': playlist_id, 'title': playlist_title})
    if not playlists:
        update.message.reply_text('No playlists were found for your search query.')
        return
    message = 'Here are the search results for your query:\n'
    for pl in playlists:
        message += f'{pl["title"]}: https://www.youtube.com/playlist?list={pl["id"]}\n'
    update.message.reply_text(message)
    context.user_data['playlists'] = playlists

def help_com(update, context):
    help_text = (
        "To search for YouTube playlists, use the /search command followed by a query.\n"
        "Example: /search beatport top 100 of house music\n"
    )
    update.message.reply_text(help_text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
def main():
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('search', search))
    dispatcher.add_handler(CommandHandler('help', help_com))
    dispatcher.add_error_handler(error)
    # Start the bot.
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()