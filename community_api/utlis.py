
def check_if_user_reacted_to_message(message_reactions: dict, user_id: int) -> bool:
    return any([user_id in reaction["users_ids"] for reaction in message_reactions.values()])
