const { Client, GatewayIntentBits, ChannelType } = require('discord.js');
const cron = require('node-cron');

// Replace with your bot's token and other IDs
const BOT_TOKEN = 'MTQxOTc4NjcyMDM5NTc4ODM2MA.GEYIZT.Ayhh6MC0EsPIbSMtsBRG25ww-aSE9u3O7KeodQ';
const GUILD_ID = '1294422826274652160';
const PARTICIPANT_ROLE_ID = '1419797988833886289';
const POSTING_CHANNEL_ID = '1422666459489763460';

const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.DirectMessages
    ]
});

client.on('ready', () => {
    console.log(`Successfully initiated Anonymous Anomaly event.`);
    
    // Set the start and end dates for the event in UTC
    const startDate = new Date('2025-10-01T00:00:00Z');
    // Set the end date to the beginning of the day AFTER the final run
    const endDate = new Date('2025-10-11T00:00:00Z');

    // Schedule the daily selection task to run at 12:00 AM every day
    cron.schedule('0 0 * * *', async () => {
        const now = new Date();
        
        // Only run if the current date is within the start and end range
        if (now >= startDate && now < endDate) {
            console.log('Daily selection process started.');
            dailySelection();
        } else {
            console.log('Event is not scheduled to run at this time.');
        }
    });
});

async function dailySelection() {
    const guild = await client.guilds.fetch(GUILD_ID);
    const role = await guild.roles.fetch(PARTICIPANT_ROLE_ID);
    
    if (!role) {
        console.log("Error: Participant role not found.");
        return;
    }

    const allParticipants = role.members.toJSON();

    if (allParticipants.length === 0) {
        console.log("No participants found with the specified role.");
        return;
    }
    
    let chosenUser = null;

    while (!chosenUser) {
        const randomIndex = Math.floor(Math.random() * allParticipants.length);
        const userAttempt = allParticipants[randomIndex];

        if (userAttempt.user.bot) {
            console.log(`Skipping ${userAttempt.user.tag} because they are a bot.`);
            continue;
        }

        try {
            await userAttempt.send({ 
                content: "You've been picked to anonymously say something. This may range from confessions to something said just to make people laugh. The server's rules still apply." 
            });
            console.log(`DM sent successfully to ${userAttempt.user.tag}. Waiting for a response...`);
            chosenUser = userAttempt;
        } catch (error) {
            if (error.code === 50007) {
                console.log(`DM failed for ${userAttempt.user.tag}. DMs are closed. Trying a new user...`);
            } else {
                console.log(`An unexpected error occurred with ${userAttempt.user.tag}:`, error);
            }
        }
    }
    
    const dmChannel = await chosenUser.createDM();
    const filter = m => m.author.id === chosenUser.id;
    const collectorOptions = {
        max: 1,
        time: 86400000,
        errors: ['time']
    };

    try {
        const collected = await dmChannel.awaitMessages(collectorOptions);
        const userMessage = collected.first();

        const postingChannel = await client.channels.fetch(POSTING_CHANNEL_ID);
        if (postingChannel && postingChannel.type === ChannelType.GuildText) {
            await postingChannel.send({
                content: `${userMessage.content}`
            });
            await chosenUser.send({
                content: `Posted to <#1422666459489763460>.`
            })
            console.log(`Posted message from ${chosenUser.user.tag} to the channel.`);
        } else {
            console.log("Posting channel not found or is not a text channel.");
        }
    } catch (error) {
        console.log(`No response received from ${chosenUser.user.tag} within the 24-hour timeout.`);
    }
}

client.login(BOT_TOKEN);