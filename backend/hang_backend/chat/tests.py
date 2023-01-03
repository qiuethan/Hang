import json

from channels.db import database_sync_to_async as dbsa
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User
from django.test import TestCase
from knox.models import AuthToken
from rest_framework.test import APIClient

from accounts.models import UserDetails
from accounts.tests import build_numbered_test_user
from chat.models import MessageChannel, GroupChat, DirectMessage, Message
from chat.routing import websocket_urlpatterns
from chat.serializers import MessageSerializer


class MessageChannelTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = build_numbered_test_user(2)

        self.user3 = build_numbered_test_user(3)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def verifyDirectMessage(self, res_dict):
        self.assertTrue({"id", "channel_type", "created_at", "message_last_sent", "users"}.issubset(res_dict))
        self.assertEqual(res_dict["channel_type"], "DM")

    def testListDirectMessage(self):
        MessageChannel.objects.create_direct_message(self.user1, self.user2)
        MessageChannel.objects.create_direct_message(self.user2, self.user3)
        response = self.client.get("/v1/chat/direct_message")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.assertEqual(len(res_dict), 1)
        self.verifyDirectMessage(res_dict[0])
        self.assertEqual(res_dict[0]["users"], [1, 2])

    def testListDirectMessageEmpty(self):
        response = self.client.get("/v1/chat/direct_message")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def testCreateDirectMessage(self):
        response = self.client.post("/v1/chat/direct_message", {"users": [1, 2]}, format="json")
        self.assertEqual(response.status_code, 201)
        res_dict = json.loads(response.content)
        self.verifyDirectMessage(res_dict)
        self.assertEqual(res_dict["users"], [1, 2])
        self.assertEqual(DirectMessage.objects.count(), 1)

        response = self.client.post("/v1/chat/direct_message", {"users": [1, 2]}, format="json")
        self.assertEqual(response.status_code, 400)

    def testCreateDirectMessageInvalidUser(self):
        response = self.client.post("/v1/chat/direct_message", {"users": [1, 4]}, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/v1/chat/direct_message", {"users": [2, 3]}, format="json")
        self.assertEqual(response.status_code, 400)

    def testCreateDirectMessageUserTooManyUsers(self):
        response = self.client.post("/v1/chat/direct_message", {"users": [1, 2, 3]},
                                    format="json")
        self.assertEqual(response.status_code, 400)

    def testRetrieveDirectMessage(self):
        channel_id = MessageChannel.objects.create_direct_message(self.user1, self.user2).id
        response = self.client.get(f"/v1/chat/direct_message/{channel_id}")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyDirectMessage(res_dict)
        self.assertEqual(res_dict["users"], [1, 2])

    def testRetrieveDirectMessageDoesNotExist(self):
        response = self.client.get("/v1/chat/direct_message/aaaaaaaaaa")
        self.assertEqual(response.status_code, 404)

    def testRetrieveDirectMessageNoAccess(self):
        channel_id = MessageChannel.objects.create_direct_message(self.user2, self.user3).id
        response = self.client.get(f"/v1/chat/direct_message/{channel_id}")
        self.assertEqual(response.status_code, 404)

    def verifyGroupChat(self, res_dict):
        self.assertTrue(
            {"id", "channel_type", "created_at", "message_last_sent", "name", "owner", "users"}.issubset(res_dict))
        self.assertEqual(res_dict["channel_type"], "GC")

    def testListGroupChat(self):
        MessageChannel.objects.create_group_chat(name="gc_12", owner=self.user1, users=[self.user1, self.user2])
        MessageChannel.objects.create_group_chat(name="gc_23", owner=self.user2, users=[self.user2, self.user3])
        response = self.client.get("/v1/chat/group_chat")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.assertEqual(len(res_dict), 1)
        self.verifyGroupChat(res_dict[0])
        self.assertEqual(res_dict[0]["owner"], 1)
        self.assertEqual(res_dict[0]["users"], [1, 2])

    def testCreateGroupChat(self):
        response = self.client.post("/v1/chat/group_chat",
                                    {"name": "gc_12", "users": [1, 2, 3]},
                                    format="json")
        self.assertEqual(response.status_code, 201)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["name"], "gc_12")
        self.assertEqual(res_dict["owner"], 1)
        self.assertEqual(res_dict["users"], [1, 2, 3])
        self.assertEqual(GroupChat.objects.count(), 1)

    def testCreateGroupChatInvalidUser(self):
        response = self.client.post("/v1/chat/group_chat",
                                    {"name": "gc_12", "users": [1, 2, 4]},
                                    format="json")
        self.assertEqual(response.status_code, 400)

    def testRetrieveGroupChat(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc_12", owner=self.user1,
                                                              users=[self.user1, self.user2]).id
        response = self.client.get(f"/v1/chat/group_chat/{channel_id}")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], 1)
        self.assertEqual(res_dict["users"], [1, 2])

    def testRetrieveGroupChatDoesNotExist(self):
        response = self.client.get("/v1/chat/group_chat/aaaaaaaaaa")
        self.assertEqual(response.status_code, 404)

    def testRetrieveGroupChatNoAccess(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc_23", owner=self.user2,
                                                              users=[self.user2, self.user3]).id
        response = self.client.get(f"/v1/chat/group_chat/{channel_id}")
        self.assertEqual(response.status_code, 404)

    def testModifyGroupChatAddUserAsOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user1,
                                                              users=[self.user1, self.user2]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 1, "users": [1, 2, 3]}, format="json")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], 1)
        self.assertEqual(res_dict["users"], [1, 2, 3])

    def testModifyGroupChatAddUserAsNonOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user2,
                                                              users=[self.user1, self.user2]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 2, "users": [1, 2, 3]}, format="json")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], 2)
        self.assertEqual(res_dict["users"], [1, 2, 3])

    def testModifyGroupChatRemoveUserAsOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user1,
                                                              users=[self.user1, self.user2, self.user3]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 1, "users": [1, 2]}, format="json")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], 1)
        self.assertEqual(res_dict["users"], [1, 2])

    def testModifyGroupChatRemoveUserAsNonOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user2,
                                                              users=[self.user1, self.user2, self.user3]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 2, "users": [1, 2]}, format="json")
        self.assertEqual(response.status_code, 400)

    def testModifyGroupChatLeaveAsOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user1,
                                                              users=[self.user1, self.user2]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 1, "users": [2]}, format="json")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], 2)
        self.assertEqual(res_dict["users"], [2])

    def testModifyGroupChatLeaveAsNonOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user2,
                                                              users=[self.user1, self.user2]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 2, "users": [2]}, format="json")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], 2)
        self.assertEqual(res_dict["users"], [2])

    def testModifyGroupChatLastUserLeaves(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user1,
                                                              users=[self.user1]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 1, "users": []}, format="json")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], None)
        self.assertEqual(res_dict["users"], [])

    def testTransferOwnershipOfGroupChatAsOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user1,
                                                              users=[self.user1, self.user2]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 2, "users": [1, 2]}, format="json")
        self.assertEqual(response.status_code, 200)
        res_dict = json.loads(response.content)
        self.verifyGroupChat(res_dict)
        self.assertEqual(res_dict["owner"], 2)
        self.assertEqual(res_dict["users"], [1, 2])

    def testTransferOwnershipOfGroupChatAsNonOwner(self):
        channel_id = MessageChannel.objects.create_group_chat(name="gc", owner=self.user2,
                                                              users=[self.user1, self.user2]).id
        response = self.client.patch(f"/v1/chat/group_chat/{channel_id}",
                                     {"owner": 1, "users": [1, 2]}, format="json")
        self.assertEqual(response.status_code, 400)


class ChatWebsocketTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test_user_1", email="test_user_1@gmail.com",
                                              password="test_user_1_password")
        self.user1.userdetails = UserDetails.objects.create(is_verified=True)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = User.objects.create_user(username="test_user_2", email="test_user_2@gmail.com",
                                              password="test_user_2_password")
        self.user2.userdetails = UserDetails.objects.create(is_verified=True)

        self.user3 = User.objects.create_user(username="test_user_3", email="test_user_3@gmail.com",
                                              password="test_user_3_password")
        self.user3.userdetails = UserDetails.objects.create(is_verified=True)

        self.channel1 = MessageChannel.objects.create_group_chat(name="gc", owner=self.user1,
                                                                 users=[self.user1, self.user2]).id
        self.channel2 = MessageChannel.objects.create_group_chat(name="gc", owner=self.user2,
                                                                 users=[self.user2, self.user3]).id

        # noinspection PyTypeChecker
        self.communicator: WebsocketCommunicator = None

    async def send_message(self, action, content):
        await self.communicator.send_json_to({
            "action": action,
            "content": content
        })

    async def verify_success(self):
        response = await self.communicator.receive_json_from()
        self.assertEqual(response, {'type': 'status', 'message': 'success'})

    async def verify_failure(self):
        response = await self.communicator.receive_json_from()
        self.assertNotEqual(response, {'type': 'status', 'message': 'success'})

    def verify_message(self, message):
        self.assertTrue(
            {"id", "user", "created_at", "updated_at", "content", "message_channel", "reply", "reactions"}
            .issubset(message.keys()))

    async def connectAndAuthenticate(self):
        self.communicator = WebsocketCommunicator(URLRouter(websocket_urlpatterns),
                                                  f"/ws/chat/{self.user1.username}/")
        connected, subprotocol = await self.communicator.connect()
        self.assertTrue(connected)
        await self.send_message("authenticate", {"token": self.token1})
        await self.verify_success()

    async def testAuthenticateInvalidToken(self):
        self.communicator = WebsocketCommunicator(URLRouter(websocket_urlpatterns),
                                                  f"/ws/chat/{self.user1.username}/")
        connected, subprotocol = await self.communicator.connect()
        self.assertTrue(connected)
        await self.send_message("authenticate", {"token": "aaaaaaaaaaaaaaaaaaaaaaaaaa"})
        await self.verify_failure()

    async def testSendMessage(self):
        await self.connectAndAuthenticate()
        await self.send_message("send_message", {
            "message_channel": self.channel1,
            "content": "a" * 2000,
            "reply": None
        })

        response = await self.communicator.receive_json_from()
        self.assertEqual(await dbsa(Message.objects.count)(), 1)
        data = await dbsa(getattr)(MessageSerializer(await dbsa(Message.objects.get)()), "data")
        self.verify_message(data)
        self.assertEqual(response, {'action': "send_message", "content": data})
        await self.verify_success()

    async def testSendMessageInvalidChannel(self):
        await self.connectAndAuthenticate()
        await self.send_message("send_message", {
            "message_channel": {
                "id": self.channel2
            },
            "content": "test_message"
        })
        await self.verify_failure()
        self.assertEqual(await dbsa(Message.objects.count)(), 0)

    async def testSendMessageOver2000Characters(self):
        await self.connectAndAuthenticate()
        await self.send_message("send_message", {
            "message_channel": {
                "id": self.channel1
            },
            "content": "a" * 2001
        })
        await self.verify_failure()
        self.assertEqual(await dbsa(Message.objects.count)(), 0)

    async def testLoadMessage(self):
        await self.connectAndAuthenticate()

        await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1, content="test_message1")
        await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1, content="test_message2")
        await dbsa(Message.objects.create)(user=self.user2, message_channel_id=self.channel2, content="test_message3")
        await dbsa(Message.objects.create)(user=self.user2, message_channel_id=self.channel2, content="test_message4")

        await self.send_message("load_message", {
            "message_channel": self.channel1
        })

        response = await self.communicator.receive_json_from()
        self.assertEqual(response["action"], "load_message")
        self.assertEqual(len(response["content"]), 2)
        self.verify_message(response["content"][0])
        self.verify_message(response["content"][1])

        await self.verify_success()

    async def testLoadMessageWithMessageId(self):
        await self.connectAndAuthenticate()

        await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1, content="test_message1")
        await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1, content="test_message2")
        await dbsa(Message.objects.create)(user=self.user2, message_channel_id=self.channel2, content="test_message3")
        await dbsa(Message.objects.create)(user=self.user2, message_channel_id=self.channel2, content="test_message4")

        await self.send_message("load_message", {
            "message_channel": self.channel1,
            "message_id": 1
        })

        response = await self.communicator.receive_json_from()
        self.assertEqual(response["action"], "load_message")
        self.assertEqual(len(response["content"]), 1)
        self.verify_message(response["content"][0])

        await self.verify_success()

    async def testLoadMessageOver20Messages(self):
        await self.connectAndAuthenticate()

        for _ in range(30):
            await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1,
                                               content="test_message")

        await self.send_message("load_message", {
            "message_channel": self.channel1
        })

        response = await self.communicator.receive_json_from()
        self.assertEqual(response["action"], "load_message")
        self.assertEqual(len(response["content"]), 20)

        for i in range(20):
            self.verify_message(response["content"][i])

        await self.verify_success()

    async def testEditMessage(self):
        await self.connectAndAuthenticate()

        await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1, content="test_message1")

        await self.send_message("edit_message", {
            "id": 1,
            "content": "a" * 2000
        })

        response = await self.communicator.receive_json_from()
        self.assertEqual(response["action"], "edit_message")
        self.verify_message(response["content"])
        data = await dbsa(getattr)(MessageSerializer(await dbsa(Message.objects.get)()), "data")
        self.assertEqual(data["content"], "a" * 2000)
        await self.verify_success()

    async def testEditMessageOver2000Characters(self):
        await self.connectAndAuthenticate()

        await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1, content="test_message1")

        await self.send_message("edit_message", {
            "id": 1,
            "content": "a" * 2001
        })
        await self.verify_failure()

    async def testEditMessageInvalidPermissions(self):
        await self.connectAndAuthenticate()

        await dbsa(Message.objects.create)(user=self.user2, message_channel_id=self.channel1, content="test_message1")

        await self.send_message("edit_message", {
            "id": 1,
            "content": "a" * 2000
        })
        await self.verify_failure()

    async def testDeleteMessage(self):
        await self.connectAndAuthenticate()

        await dbsa(Message.objects.create)(user=self.user1, message_channel_id=self.channel1, content="test_message1")

        await self.send_message("delete_message", {
            "id": 1,
        })

        response = await self.communicator.receive_json_from()
        self.assertEqual(response["action"], "delete_message")
        self.assertEqual(response["content"]["id"], 1)
        await self.verify_success()

    async def testDeleteMessageInvalidPermissions(self):
        await self.connectAndAuthenticate()

        await dbsa(Message.objects.create)(user=self.user2, message_channel_id=self.channel1, content="test_message1")

        await self.send_message("delete_message", {
            "id": 1,
        })
        await self.verify_failure()
