require('dotenv').config();
const { Client, GatewayIntentBits, Partials } = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers
    ],
    partials: [Partials.Channel]
});

const NOTIFY_CHANNEL_ID = process.env.NOTIFY_CHANNEL_ID;

client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}`);
});

// Notify channel when a file is uploaded (example function)
function notifyUpload(filename, uploader, fileUrl) {
    const channel = client.channels.cache.get(NOTIFY_CHANNEL_ID);
    if (channel) {
        channel.send(`:inbox_tray: **File uploaded:** [${filename}](${fileUrl}) by ${uploader}`);
    }
}

// Basic moderation commands
client.on('messageCreate', async (message) => {
    if (!message.guild || message.author.bot) return;
    const args = message.content.trim().split(/ +/);
    const command = args.shift().toLowerCase();

    // Kick command
    if (command === '!kick' && message.member.permissions.has('KickMembers')) {
        const member = message.mentions.members.first();
        if (member) {
            await member.kick();
            message.channel.send(`:boot: Kicked ${member.user.tag}`);
        } else {
            message.channel.send('Please mention a user to kick.');
        }
    }

    // Ban command
    if (command === '!ban' && message.member.permissions.has('BanMembers')) {
        const member = message.mentions.members.first();
        if (member) {
            await member.ban();
            message.channel.send(`:hammer: Banned ${member.user.tag}`);
        } else {
            message.channel.send('Please mention a user to ban.');
        }
    }

    // Purge command
    if (command === '!purge' && message.member.permissions.has('ManageMessages')) {
        const count = parseInt(args[0], 10);
        if (!isNaN(count) && count > 0 && count <= 100) {
            await message.channel.bulkDelete(count, true);
            message.channel.send(`:wastebasket: Deleted ${count} messages.`);
        } else {
            message.channel.send('Please specify a number between 1 and 100.');
        }
    }
});

client.login(process.env.DISCORD_TOKEN);

module.exports = { notifyUpload };
