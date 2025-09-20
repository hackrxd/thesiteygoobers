require('dotenv').config();
const { Client, GatewayIntentBits, Partials } = require('discord.js');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

// Add DM handler to update website quote
async function updateWebsiteQuote(content, author) {
    try {
        const response = await fetch('http://localhost:3000/api/webtext', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: content,
                author: author
            })
        });
        return response.ok;
    } catch (error) {
        console.error('Error updating quote:', error);
        return false;
    }
}

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.DirectMessages // Add DM intent
    ],
    partials: [
        Partials.Channel,
        Partials.Message // Need this for DMs
    ]
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

// Consolidate all message handling into a single event listener
client.on('messageCreate', async (message) => {
    // 1. Handle DMs
    if (!message.guild && !message.author.bot) {
        const success = await updateWebsiteQuote(message.content, message.author.tag);
        if (success) {
            message.reply('Quote updated successfully! Check the website to see it.');
        } else {
            message.reply('Sorry, there was an error updating the quote. Please try again later.');
        }
        return; // Important: Stop processing if it's a DM
    }

    // 2. Handle server messages and commands
    if (message.author.bot) return; // Ignore messages from other bots
    
    const args = message.content.trim().split(/ +/);
    const command = args.shift().toLowerCase();

    // Kick command
    if (command === '!kick' && message.member && message.member.permissions.has('KickMembers')) {
        const member = message.mentions.members.first();
        if (member) {
            await member.kick();
            message.channel.send(`:boot: Kicked ${member.user.tag}`);
        } else {
            message.channel.send('Please mention a user to kick.');
        }
    }

    // Ban command
    if (command === '!ban' && message.member && message.member.permissions.has('BanMembers')) {
        const member = message.mentions.members.first();
        if (member) {
            await member.ban();
            message.channel.send(`:hammer: Banned ${member.user.tag}`);
        } else {
            message.channel.send('Please mention a user to ban.');
        }
    }

    // Purge command
    if (command === '!purge' && message.member && message.member.permissions.has('ManageMessages')) {
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