import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os

from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, ssl
from twisted.logger import Logger, textFileLogObserver
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from pymarkov import pymarkov

import Commands

class DiscordFactory(ClientFactory):

	def __init__(self, accessList, ircAddress):
		self.accessList = accessList

		ircAddress, ircPort = ircAddress

		if "+" in ircPort:
			ircPort = int(ircPort[1:])

			sslOptions = ssl.CertificateOptions()
			reactor.connectSSL(ircAddress, ircPort, self, sslOptions)

		else:
			ircPort = int(ircPort)

			reactor.connectTCP(ircAddress, ircPort, self)

		reactor.run()

	def buildProtocol(self, addr):
		return Discord(self.accessList)

class Discord(IRCClient):

	nickname = "discord"
	realname = "Discord"
	username = "discord"
	versionName = "Discord"
	versionNum = "0.01"

	magicFile = "true.txt"

	def __init__(self, accessList):
		self.logger = Logger(observer=textFileLogObserver(sys.stdout))

		self.accessList = [nick.lower() for nick in accessList]

		if not os.path.exists(self.magicFile):
			self.logger.info("Creating magic file")

			try:
				with open(self.magicFile, "a"):
					pass

			except Exception as ex:
				self.logger.error("Unable to create magic file! {0}".format(ex.message))
				reactor.stop()

		self.markovGenerator = pymarkov.MarkovChainGenerator(self.magicFile)

		self.channels = []
		self.channelPhrasers = {}

		self.logger.debug("Discord initialized")

		# Maybe add hook/plugin system here?

		self.commands = Commands.Commands(self)		

	def removeChannel(self, channel):
		try:
			self.channels.remove(channel)

			self.channelPhrasers[channel].stop()
			
			del self.channelPhrasers[channel]

		except:
			self.logger.error("Error removing {channel} from collection", channel=channel)

	def insertPhrase(self, phrase):
		try:
			with open(self.magicFile, "a") as magicFile:
				magicFile.write("{0}\n".format(phrase))

			try:
				file, ext = os.path.splitext(self.magicFile)
				os.remove("{0}-pickled{1}".format(file, ext))

				# Simply re-populating the dictionary isn't enough for some reason
				self.markovGenerator = pymarkov.MarkovChainGenerator(self.magicFile, 4)

			except IOError as ex:
				self.logger.error("Unable to delete pickled file. {0}".format(ex.message))			

		except Exception as ex:
			self.logger.error("Unable to insert phrase into magic file! {0}".format(ex.message))

	def kickedFrom(self, channel, kicker, message):
		self.removeChannel(channel)

		self.logger.info("Kicked from {channel} by {kicker}", channel=channel, kicker=kicker)

	def left(self, channel):
		self.removeChannel(channel)

		self.logger.info("Left {channel}", channel=channel)

	def handleMessage(self, user, channel, message):
		senderNickname = user.split("!")[0]

		if message.startswith("~reload") and senderNickname in self.accessList:
			self.logger.info("Reloading commands module")
			self.say(channel, "Reloading.")

			try:
				commandsModule = reload(Commands)
				self.commands = commandsModule.Commands(self)

			except Exception as e:
				self.say(channel, "Failed to load commands module - {0}".format(e.message))

		elif message.startswith("~"):
			# Don't log commands to the brain
			commandMessage = message[1:]

			self.commands.handleCommand(user, channel, commandMessage)

		else:
			self.logger.info("Adding {message!r} to brain", message=message)

			# Avoid storing anything with the bot's name in it
			brainMessage = message.strip(self.nickname)

			self.insertPhrase(brainMessage)

			try:
				randomPhrase = self.markovGenerator.generate_sentence().strip(self.nickname)

				if self.nickname in message and channel.startswith("#") and self.channelPhrasers[channel].running:
					phrase = "{0}, {1}".format(senderNickname, randomPhrase)

					self.say(channel, phrase)

				elif channel == self.nickname:
					self.logger.debug("Sending message to {nickname}", nickname=senderNickname)

					self.msg(senderNickname, randomPhrase)

				else:
					pass

			except IndexError as generationError:
				self.logger.error(generationError.message)

	def privmsg(self, user, channel, message):
		self.logger.info("Received message from {user} in {channel}", user=user, channel=channel)

		# deferToThread(self.handleMessage, user, channel, message)
		self.handleMessage(user, channel, message)

	def signedOn(self):
		self.logger.info("Signed on")

		self.join("#bots")

	def joined(self, channel):
		self.channels.append(channel)

		self.logger.info("Joined channel {channel!r}", channel=channel)

		channelPhraser = LoopingCall(self.sayRandomPhrase, channel)
		reactor.callLater(2, channelPhraser.start, 600)

		self.channelPhrasers[channel] = channelPhraser

	def sayRandomPhrase(self, channel):
		try:
			randomPhrase = self.markovGenerator.generate_sentence()
			self.say(channel, randomPhrase)

		except IndexError:
			pass  # Out of range error (doesn't matter anymore)


scriptFile, ircAddress, ircPort = sys.argv

DiscordFactory(["arthur"], (ircAddress, ircPort))
