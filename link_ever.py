

async def link_message(user_id, nickname) -> any:
	link = f"<b><a href='tg://openmessage?user_id={user_id}'>{nickname}</a></b>"
	return link