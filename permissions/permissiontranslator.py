from yukari.permissions.permissions import DiscordPermission

_discord_permission_strings = {
    DiscordPermission.create_instant_invite: "permissions.create_invite",
    DiscordPermission.kick_members: "permission.kick_members",
    DiscordPermission.ban_members: "permission.ban_members",
    DiscordPermission.administrator: "permission.administrator",
    DiscordPermission.manage_channels: "permission.manage_channels",
    DiscordPermission.manage_guild: "permission.manage_guild",
    DiscordPermission.add_reactions: "permission.add_reactions",
    DiscordPermission.view_audit_log: "permission.view_audit_log",
    DiscordPermission.priority_speaker: "permission.priority_speaker",
    DiscordPermission.stream: "permission.stream_in_voice",
    DiscordPermission.read_messages: "permission.read_messages",
    DiscordPermission.view_channel: "permission.view_channel",
    DiscordPermission.send_messages: "permission.send_messages",
    DiscordPermission.send_tts_messages: "permission.send_tts_messages",
    DiscordPermission.manage_messages: "permission.manage_messages",
    DiscordPermission.embed_links: "permission.embed_links",
    DiscordPermission.attach_files: "permission.attach_files",
    DiscordPermission.read_message_history: "permission.read_message_history",
    DiscordPermission.mention_everyone: "permission.mention_everyone",
    DiscordPermission.external_emojis: "permission.external_emojis",
    DiscordPermission.use_external_emojis: "permission.external_emojis",
    DiscordPermission.view_guild_insights: "permission.view_guild_insights",
    DiscordPermission.connect: "permission.voice_connect",
    DiscordPermission.speak: "permission.voice_speak",
    DiscordPermission.mute_members: "permission.voice_mute_members",
    DiscordPermission.deafen_members: "permission.voice_deafen_members",
    DiscordPermission.move_members: "permission.voice_move_members",
    DiscordPermission.use_voice_activation: "permission.use_voice_activation",
    DiscordPermission.change_nickname: "permission.change_nickname",
    DiscordPermission.manage_nicknames: "permission.manage_nicknames",
    DiscordPermission.manage_roles: "permission.manage_roles",
    DiscordPermission.manage_permissions: "permission.manage_roles",
    DiscordPermission.manage_webhooks: "permission.manage_webhooks",
    DiscordPermission.manage_emojis: "permission.manage_emojis"
}

def translate_permission(discord_permission):
    # TODO: issue #45
    pass
