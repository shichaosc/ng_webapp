;(function() {
var ChatMessage, ChatUI, Chat, ChatWidget, opentok_text_chat;
ChatMessage = function () {
  /**
   * A convinient representation of a chat message.
   *
   * @class ChatMessage
   * @constructor
   * @param {String} senderId A unique id to identify the origin of the message.
   * @param {String} senderAlias A name to be displayed as the author of the
   * message.
   * @param {String} text The contents of the message.
   */
  function ChatMessage(senderId, senderAlias, text) {
    Object.defineProperties(this, {
      /**
       * A unique id to identify the origin of the message.
       *
       * @property senderId
       * @type String
       * @readOnly
       */
      senderId: { value: senderId },
      /**
       * A name to be displayed as the author of the message.
       *
       * @property senderAlias
       * @type String
       * @readOnly
       */
      senderAlias: { value: senderAlias },
      /**
       * The contents of the message.
       *
       * @property text
       * @type String
       * @readOnly
       */
      text: { value: text },
      /**
       * The moment the message was created at.
       *
       * @property senderId
       * @type Date
       * @readOnly
       */
      dateTime: { value: new Date() }
    });
  }
  return ChatMessage;
}();
ChatUI = function (ChatMessage) {
  var uiLayout = [
    '<div class="ot-bubbles" style="max-height: 50;overflow-y: scroll;">',
    '</div>',
    '<div class="ot-input">',
    '  <div>',
    '    <p class="ot-error-zone" hidden>Error sending the message!</p>',
    '    <p class="ot-new-messages" hidden>\u25BE&nbsp;New messages</p>',
    '    <textarea placeholder="Send a message&hellip;" class="ot-composer fluid">' + '</textarea>',
    '    <div class="ot-bottom-line">',
    '      <p class="ot-character-counter"><span></span> characters left</p>',
    '      <button class="ot-send-button">Send&nbsp;\u27E9</button>',
    '    </div>',
    '  </div>',
    '</div>'
  ].join('\n');
  var bubbleLayout = [
    '<div>',
    '  <header class="ot-bubble-header">',
    '    <p class="ot-message-sender"></p>',
    //'    <time class="ot-message-timestamp"></time>',
    '  </header>',
    '</div>'
  ].join('\n');
  /**
   * User interface for a basic chat client.
   *
   * The UI display bubbles representing the chat activity in the conversation
   * area. An input area displays the remaining characters and allows to send
   * messages by hitting enter or clicking on the send button. To add a normal
   * break-line you can press the `shift + enter` combination.
   *
   * The conversation area groups messages separated no more than 2 minutes
   * (although this can be configured) and allow the user to review past
   * history even if receiving new messages.
   *
   * The chat UI can be placed inside any element by providing a `container`
   * and it will fill the container box.
   *
   * @class ChatUI
   * @constructor
   * @param {Object} [options] Hash with customizing properties.
   * @param {String} [options.container='body'] CSS selector representing the
   * container for the chat.
   * @param {String} [options.senderId] Unique id for this client. It defaults
   * in a random number.
   * @param {String} [options.senderAlias='me'] Alias to be displayed for this
   * client.
   * @param {Number} [options.maxTextLength=1000] Maximum length of the message.
   * @param {Number} [options.groupDelay=120000] Time in milliseconds to be
   * passed for the UI to separate the messages in different bubbles.
   * @param {Number} [options.timeout=5000] Time in milliseconds before
   * informing about a malfunction while sending the message.
   */
  function ChatUI(options) {
    options = options || {};
    this.senderId = options.senderId || ('' + Math.random()).substr(2);
    this.senderAlias = options.senderAlias || 'me';
    this.maxTextLength = options.maxTextLength || 1000;
    this.groupDelay = options.groupDelay || 2 * 60 * 1000;
    // 2 min
    this.timeout = options.timeout || 5000;
    this._watchScrollAtTheBottom = this._watchScrollAtTheBottom.bind(this);
    this._messages = [];
    this._setupTemplates();
    this._setupUI(options.container);
    this._updateCharCounter();
  }
  ChatUI.prototype = {
    constructor: ChatUI,
    _setupTemplates: function () {
      this._bubbleTemplate = document.createElement('section');
      this._bubbleTemplate.innerHTML = bubbleLayout;
      this._bubbleTemplate.classList.add('ot-bubble');
    },
    _setupUI: function (parent) {
      parent = document.querySelector(parent) || document.body;
      var chatView = document.createElement('section');
      chatView.innerHTML = uiLayout;
      chatView.classList.add('ot-textchat');
      var sendButton = chatView.querySelector('.ot-send-button');
      var composer = chatView.querySelector('.ot-composer');
      var charCounter = chatView.querySelector('.ot-character-counter > span');
      var errorZone = chatView.querySelector('.ot-error-zone');
      var newMessages = chatView.querySelector('.ot-new-messages');
      this._composer = composer;
      this._sendButton = sendButton;
      this._charCounter = charCounter;
      this._bubbles = chatView.firstElementChild;
      this._errorZone = errorZone;
      this._newMessages = newMessages;
      // XXX: It's already bound in the constructor
      this._bubbles.onscroll = this._watchScrollAtTheBottom;
      this._sendButton.onclick = this._sendMessage.bind(this);
      this._composer.onkeyup = this._updateCharCounter.bind(this);
      this._composer.onkeydown = this._controlComposerInput.bind(this);
      this._newMessages.onclick = this._goToNewMessages.bind(this);
      parent.appendChild(chatView);
    },
    _watchScrollAtTheBottom: function () {
      if (this._isAtBottom()) {
        this._hideNewMessageAlert();
      }
    },
    _sendMessage: function () {
      var _this = this;
      var contents = this._composer.value;
      if (contents.length > _this.maxTextLength) {
        _this._showTooLongTextError();
      } else {
        _this._hideErrors();
        if (typeof _this.onMessageReadyToSend === 'function') {
          _this.disableSending();
          var timeout = setTimeout(function () {
            _this._showError();
            _this.enableSending();
          }, _this.timeout);
          var sent = _this.onMessageReadyToSend(contents, function (err) {
            clearTimeout(timeout);
            if (err) {
              _this._showError();
            } else {
              _this.addMessage(new ChatMessage(_this.senderId, _this.senderAlias, contents));
              _this._composer.value = '';
              _this._updateCharCounter();
              _this._hideErrors();
            }
            _this.enableSending();
          });
        }
      }
    },
    _showTooLongTextError: function () {
      this._charCounter.parentElement.classList.add('error');
    },
    _hideTooLongTextError: function () {
      this._charCounter.parentElement.classList.remove('error');
    },
    _showNewMessageAlert: function () {
      this._newMessages.removeAttribute('hidden');
    },
    _hideNewMessageAlert: function () {
      this._newMessages.hidden = true;
    },
    _showError: function () {
      this._errorZone.hidden = false;
    },
    _hideErrors: function () {
      this._errorZone.hidden = true;
      this._hideTooLongTextError();
    },
    _controlComposerInput: function (evt) {
      var isEnter = evt.which === 13 || evt.keyCode === 13;
      if (!evt.shiftKey && isEnter) {
        evt.preventDefault();
        this._sendMessage();
      }
    },
    _goToNewMessages: function () {
      this._scrollToBottom();
      this._hideNewMessageAlert();
    },
    _updateCharCounter: function () {
      var remaining = this.maxTextLength - this._composer.value.length;
      var isValid = remaining >= 0;
      if (isValid) {
        this._hideTooLongTextError();
      } else {
        this._showTooLongTextError();
      }
      this._charCounter.textContent = remaining;
    },
    /**
     * Adds a message to the conversation.
     *
     * @method addMessage
     * @param {ChatMessage} message The message to be displayed.
     */
    addMessage: function (message) {
      var shouldGroup = this._shouldGroup(message);
      var shouldScroll = this._shouldScroll();
      this[shouldGroup ? '_groupBubble' : '_addNewBubble'](message);
      if (shouldScroll) {
        this._scrollToBottom();
      } else {
        this._showNewMessageAlert();
      }
      this._messages.push(message);
    },
    /**
     * Transform the message before displaying it in the conversation. The
     * result of this method is considered safe html so be careful and take
     * care.
     *
     * @method renderMessage
     * @param {String} raw Original contents recovered from the message.
     * @param {Boolean} isGrouping If `true` the content will be merged with
     * the previous bubble.
     * @return {String} Valid HTML to be displayed in the conversation.
     */
    renderMessage: function (raw, isGrouping) {
      return raw;
    },
    /**
     * Enable input area and sending button.
     *
     * @method enableSending
     */
    enableSending: function () {
      this._sendButton.removeAttribute('disabled');
      this._composer.removeAttribute('disabled');
      this._composer.focus();
    },
    /**
     * Disable input area and sending button.
     *
     * @method disableSending
     */
    disableSending: function () {
      this._sendButton.disabled = true;
      this._composer.disabled = true;
    },
    _shouldGroup: function (message) {
      if (this._lastMessage && this._lastMessage.senderId === message.senderId) {
        var reference = this._lastMessage.dateTime.getTime();
        var newDate = message.dateTime.getTime();
        return newDate - reference < this.groupDelay;
      }
      return false;
    },
    _shouldScroll: function () {
      return this._isAtBottom();
    },
    _isAtBottom: function () {
      var bubbles = this._bubbles;
      return bubbles.scrollHeight - bubbles.scrollTop === bubbles.clientHeight;
    },
    _scrollToBottom: function () {
      this._bubbles.scrollTop = this._bubbles.scrollHeight;
    },
    _groupBubble: function (message) {
      var contents = this.renderMessage(message.text, true);
      this._lastBubble.appendChild(this._getBubbleContent(contents));
      //this._lastTimestamp.textContent = this.humanizeDate(message.dateTime);
    },
    _addNewBubble: function (message) {
      this._bubbles.appendChild(this._getBubble(message));
    },
    get _lastMessage() {
      return this._messages[this._messages.length - 1];
    },
    get _lastBubble() {
      return this._bubbles.lastElementChild.querySelector('div');
    },
    get _lastTimestamp() {
      return this._bubbles.lastElementChild.querySelector('.ot-message-timestamp');
    },
    _getBubbleContent: function (safeHtml) {
      var div = document.createElement('DIV');
      div.classList.add('ot-message-content');
      div.innerHTML = safeHtml;
      return div;
    },
    _getBubble: function (message) {
      var bubble = this._bubbleTemplate.cloneNode(true);
      var wrapper = bubble.querySelector('div');
      var sender = wrapper.querySelector('.ot-message-sender');
      
      //var timestamp = wrapper.querySelector('.ot-message-timestamp');
      // Sender & alias
      bubble.dataset.senderId = message.senderId;
      if (message.senderId === this.senderId) {
        bubble.classList.add('mine');
      }
      sender.textContent = message.senderAlias;
      // Content
      var contents = this.renderMessage(message.text, false);
      wrapper.appendChild(this._getBubbleContent(contents));
      // Timestamp is disabled
      //timestamp.dateTime = message.dateTime.toISOString();
      //timestamp.textContent = this.humanizeDate(message.dateTime);
      return bubble;
    },
    /**
     * Called when displaying a message to human format the date.
     *
     * @method humanizeDate
     * @param {Date} date The date from the message.
     * @return {String} Human friendly representation for the passed date.
     */
    humanizeDate: function (date) {
      var hours = date.getHours();
      var isAM = hours < 12;
      var hours12 = hours > 12 ? hours - 12 : hours;
      var minutes = date.getMinutes();
      minutes = (minutes < 10 ? '0' : '') + minutes;
      return hours + ':' + minutes + (isAM ? ' AM' : ' PM');
    }
  };
  return ChatUI;
}(ChatMessage);
Chat = function () {
  /**
   * OpenTok signal based Chat client.
   *
   * @class Chat
   * @constructor
   * @param {Object} options Hash with configuration options.
   * @param {Session} options.session OpenTok connected session for the chat.
   * @param {String} [options.signalName='TextChat'] The name for the signal to
   * be used to transport messages. Leave as it is to ensure compatibility with
   * the iOS and Android components or change to provide your own.
   */
  function Chat(options) {
    if (!options || !options.session) {
      throw new Error('No session provided.');
    }
    this._session = options.session;
    var signalName = options.signalName || 'TextChat';
    this._session.on('signal:' + signalName, this._handleChatSignal.bind(this));
    Object.defineProperty(this, 'signalName', { value: signalName });
  }
  Chat.prototype = {
    constructor: Chat,
    /**
     * Sends a message though the chat.
     *
     * @method send
     * @param {String} text Contents of the message.
     * @param {Function} callback Called once the signal has been sent. If there
     * is an error while sending, the callback is passed the error as first
     * parameter.
     * @async
     */
    send: function (text, callback) {
      var signal = this._getMessageSignal(text);
      this._session.signal(signal, callback);
    },
    /**
     * Called when receiving a new message from the chat.
     *
     * @method onMessageReceived
     * @param {String} contents The contents from the received message.
     * @param {Connection} from OpenTok `Connection` representing the
     * participant sending the message.
     */
    onMessageReceived: function (contents, from) {
    },
    _handleChatSignal: function (signal) {
      var me = this._session.connection.connectionId;
      var from = signal.from.connectionId;
      if (from !== me) {
        var handler = this.onMessageReceived;
        if (handler && typeof handler === 'function') {
          handler(signal.data, signal.from);
        }
      }
    },
    _getMessageSignal: function (text) {
      return {
        type: this.signalName,
        data: text
      };
    }
  };
  return Chat;
}();
ChatWidget = function (Chat, ChatUI, ChatMessage) {
  // This regular expression detect text fragments looking like URLs.
  var links = /https?\:\/\/[^.]+\..+/g;
  /**
   * An HTML widget enabling basic chat capabilities. Pass a `session` object
   * to the `options` hash. It's not mandatory for the session to be connected
   * but the chat won't allow the user until the session is connected.
   *
   * @class ChatWidget
   * @constructor
   * @param {Object} options A hash with the union of the options for
   * {{#crossLink "Chat"}}{{/crossLink}} and
   * {{#crossLink "ChatUI"}}{{/crossLink}} constructors to customize several
   * aspects of the chat behaviour and internals.
   */
  // The `ChatWidget` class combines the `ChatUI` and `ChatMessage` UI classes
  // plus the `Chat` library to provide a functional Chat widget.
  function ChatWidget(options) {
    if (!options || !options.session) {
      throw new Error('The key session must be present and set to a valid OpenTok session.');
    }
    this._chatBox = new ChatUI(options);
    // Overriding the `ChatUI#renderMessage()` function you can transform
    // the contents of a message before showing them into the conversation.
    this._chatBox.renderMessage = this.renderMessage.bind(this);
    // If the session is connected, create the chat session...
    if (options.session.connection) {
      this._start(options);
    }  // ...if not, simply wait for the session to be connected, then create
       // the chat session.
    else {
      options.session.once('sessionConnected', this._start.bind(this, options));
    }
    this._chatBox.disableSending();
  }
  ChatWidget.prototype = {
    constructor: ChatWidget,
    // Connect the chat to the session provided in the `options` object.
    _start: function (options) {
      if (!this._chat) {
        this._chat = new Chat(options);
        // Received messages are handled by the library...
        this._chat.onMessageReceived = this.onMessageReceived.bind(this);
        // ...while sending messages is something controlled by the UI.
        this._chatBox.onMessageReadyToSend = this.onMessageReadyToSend.bind(this);
        // This set the sender information, their id to group messages and their
        // alias to show to other users.
        this._chatBox.senderId = options.session.connection.connectionId;
        
        var connData = jQuery.parseJSON( options.session.connection.data );
        var username = connData.username;	
        this._chatBox.senderAlias = username;
        // Finally, enable message area and send buttons.
        this._chatBox.enableSending();
      }
    },
    /**
     * Called when the user clicks on the send button. It will received the
     * contents from the input area and a callback to call once it finishes to
     * send the message and it can be displayed in the conversation area.
     *
     * @method onMessageReadyToSend
     * @param {String} contents Contents of the input area at the moment the
     * user clicked on the send button.
     * @param {Function} callback Function to call once the message is ready
     * to be displayed in the conversation area (usually after it was
     * successfully sent). Pass no parameters to denote success and some
     * error to indicate a failure.
     */
    // After the user click on the send button, simply send the contents through
    // the `Chat` instance.
    onMessageReadyToSend: function (contents, callback) {
      this._chat.send(contents, callback);
    },
    /**
     * Called when the chat receives a message. It extracts the proper id and
     * alias from the connection representing the participant that sent the
     * message and add it to the conversation.
     *
     * @method onMessageReceived
     * @param {String} contents The very same raw contents received through
     * the chat.
     * @param {Connection} from The OpenTok connection object representing
     * the participant sending the message.
     */
    // After a message is received, simply create a new `ChatMessage` instance
    // and add it to the UI.
    onMessageReceived: function (contents, from) {
      var connData = jQuery.parseJSON( from.data );
      var username = connData.username;	
      var message = new ChatMessage(from.connectionId, username, contents);
      this._chatBox.addMessage(message);
      if ($('#chat').attr('class') == 'hidden')
        $('.notification').css('display', '');
    },
    /**
     * Transform the text from the message into the actual content to be
     * displayed. This case allow multiline messages and recognize urls.
     *
     * @method renderMessage
     * @param {String} raw The original message contents.
     */
    // Transformations implemented by the default widget include detecting URLs
    // and allowing multiline messages.
    renderMessage: function (raw) {
      var output;
      // Allow multiline
      output = raw.replace(/(\r\n|\r|\n)/g, '<br/>');
      // Detect links
      output = output.replace(links, function (href) {
        return '<a href="' + href + '" target="_blank">' + href + '</a>';
      });
      return output;
    }
  };
  return ChatWidget;
}(Chat, ChatUI, ChatMessage);
opentok_text_chat = function (Chat, ChatUI, ChatMessage, ChatWidget) {
  window.OTSolution = window.OTSolution || {};
  window.OTSolution.TextChat = {
    Chat: Chat,
    ChatUI: ChatUI,
    ChatMessage: ChatMessage,
    ChatWidget: ChatWidget
  };
}(Chat, ChatUI, ChatMessage, ChatWidget);
}());