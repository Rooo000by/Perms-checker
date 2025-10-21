import 'dotenv/config';
import { Client, GatewayIntentBits, Partials, REST, Routes, EmbedBuilder, PermissionsBitField } from 'discord.js';
import express from 'express';

const app = express();
const port = process.env.PORT || 10000;

// Setup basic webserver for Render health checks
app.get('/', (req, res) => {
  res.send('Bot is running!');
});

app.listen(port, () => {
  console.log(`Express server started on port ${port}`);
});

// Discord client with intents to read guild roles
const client = new Client({
  intents: [GatewayIntentBits.Guilds],
  partials: [Partials.GuildMember]
});

// Register slash command on bot startup
const commands = [
  {
    name: 'perms',
    description: 'Show all roles and their permissions on this server',
  }
];

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_BOT_TOKEN);

async function registerCommands() {
  try {
    console.log('Registering slash commands...');
    if (!process.env.GUILD_ID) {
      // Register globally (can take up to 1 hour to update)
      await rest.put(
        Routes.applicationCommands(process.env.CLIENT_ID),
        { body: commands }
      );
      console.log('Registered global commands.');
    } else {
      // Register per guild (instant update, good for development)
      await rest.put(
        Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
        { body: commands }
      );
      console.log('Registered guild commands.');
    }
  } catch (error) {
    console.error(error);
  }
}

client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag}`);
  await registerCommands();
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isCommand()) return;

  if (interaction.commandName === 'perms') {
    const guild = interaction.guild;
    if (!guild) {
      await interaction.reply({ content: 'This command can only be used in a server.', ephemeral: true });
      return;
    }

    const embed = new EmbedBuilder()
      .setTitle(`Roles and Permissions in ${guild.name}`)
      .setColor(0x0099ff);

    // For each role, get allowed permissions as strings
    for (const role of guild.roles.cache.values()) {
      const perms = [];

      for (const [permName, hasPerm] of Object.entries(role.permissions.toJSON())) {
        if (hasPerm) perms.push(permName.replace(/_/g, ' ').toLowerCase().replace(/\b(\w)/g, c => c.toUpperCase()));
      }

      embed.addFields({ name: role.name, value: perms.length ? perms.join(', ') : 'No Permissions', inline: false });
    }

    await interaction.reply({ embeds: [embed] });
  }
});

client.login(process.env.DISCORD_BOT_TOKEN);
