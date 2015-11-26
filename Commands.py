from time import time

class Commands(object):

	# TODO: define "logger" property using self.bot's
	def __init__(self, bot):
		self.bot = bot

		self.commands = {
			"ping": self.handlePing,
			"access": self.handleAccess,
			"phraser": self.handlePhraser,
			"join": self.handleJoin,
			"leave": self.handleLeave
		}

		# Keeps track of the last time people have used commands
		# Nickname as key, list containing count and timestamp as value
		self.commandHistory = {}

		self.bot.logger.info("Commands module initialized")

	def handlePhraser(self, user, channel, args):
		nickname = user.split("!")[0].lower()

		if nickname not in self.bot.accessList:
			self.bot.msg(nickname, "You are not authorized to perform that command.")

		else:
			try:
				command = args[0].lower()
				targetChannel = args[1]

				try:
					if command == "start":
						self.bot.channelPhrasers[targetChannel].start(600)

						self.bot.msg(nickname, "Phraser started for channel {0}".format(targetChannel))

					elif command == "stop":
						self.bot.channelPhrasers[targetChannel].stop()

						self.bot.msg(nickname, "Phraser stopped for channel {0}".format(targetChannel))

					else:
						self.bot.msg(nickname, "Invalid command usage - start or stop.")

				except KeyError:
					self.bot.msg(nickname, "Phraser for channel {0} not found - remember that channel names are case sensitive."
							.format(targetChannel))

			except Exception as ex:
				self.bot.msg(nickname, "Unknown error when handling phraser command - {0}".format(ex.message))

	def handleAccess(self, user, channel, args):
		nickname = user.split("!")[0].lower()

		if nickname not in self.bot.accessList:
			self.bot.msg(nickname, "You are not authorized to perform that command.")

		else:
			try:
				command = args[0].lower()
				originalNickname = args[1]
				accessNickname = args[1].lower()

				if command == "del":
					try:
						self.bot.accessList.remove(accessNickname)
						self.bot.msg(nickname, "{0} was successfully removed from the access list.".format(originalNickname))

					except ValueError as ex:
						self.bot.msg(nickname, "That user doesn't exist within the access list.")

				elif command == "add":
					if accessNickname in self.bot.accessList:
						self.bot.msg(nickname, "That user already has access.")

					else:
						self.bot.accessList.append(accessNickname)
						self.bot.msg(nickname, "{0} was successfully added to the access list.".format(originalNickname))

				else:
					self.bot.msg(nickname, "Invalid command usage.")

			except:
				self.bot.msg(nickname, "Unable to execute command - maybe you're missing an arguemnt?")

	def handleLeave(self, user, channel, args):
		nickname = user.split("!")[0].lower()

		if nickname in self.bot.accessList:
			channelToLeave = args[0]
			self.bot.leave(channelToLeave)

	def handleJoin(self, user, channel, args):
		nickname = user.split("!")[0].lower()

		if nickname in self.bot.accessList:
			channelToJoin = args[0]
			self.bot.join(channelToJoin)

	def handlePing(self, user, channel, args):
		self.bot.logger.debug("Handling PING command")

		data = "".join(args)

		self.bot.say(channel, "Pong {0}".format(data))

	def allowCommand(self, nickname):
		if nickname in self.commandHistory:
			commandCount, lastCommandTime = self.commandHistory[nickname]

			# If they've executed less than three commands within the past second
			if commandCount < 3 and lastCommandTime <= time() - 1:
				# Proceed
				self.bot.logger.debug("Less than three commands within the past second")

				return True

			# If they've executed more than or equal to three commands
			# within the past six seconds
			elif commandCount >= 3 and lastCommandTime > time() - 6:
				self.bot.logger.debug("Greater than or equal to three commands within the past six seconds")

				return False

			# They exceeded the limit, but it's been past six seconds
			else:
				self.bot.logger.debug("Command history count reset for {nickname}!", nickname=nickname)
				self.commandHistory[nickname][0] = 0

				return True

		else:
			return True

	def recordCommand(self, nickname):
		if nickname in self.commandHistory:
			commandCount, lastCommandTime = self.commandHistory[nickname]
		else:
			commandCount = 0

		commandCount += 1

		self.commandHistory[nickname] = [commandCount, time()]

	def handleCommand(self, user, channel, message):
		self.bot.logger.debug("Handling command with message {message}", message=message)

		tokens = message.split(" ")
		command = tokens[0].lower()
		args = tokens[1:]		

		if command in self.commands:
			# The reason this is defined here is because there isn't a point
			# in defining it if we're not being commanded
			nickname = user.split("!")[0].lower()

			if self.allowCommand(nickname):
				self.commands[command](user, channel, args)

				self.recordCommand(nickname)

		else:
			self.bot.logger.info("Invalid command attempt: {command}", command=command)
