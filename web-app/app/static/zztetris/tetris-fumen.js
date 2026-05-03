(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
    const { decoder, encoder, Page, Field } = require('tetris-fumen');

    function toPage(board) {
        FieldString = '';
        for (let row = 20; row < board.length; row++) {
            for (let col = 0; col < 10; col++) {
                if (board[row][col]['t'] == 1 && board[row][col]['c'] != '') {
                    FieldString += board[row][col]['c'];
                } else FieldString += '_';
            }
        }
        return {
            field: Field.create(FieldString),
        };
    }

    window.decode = function decode(fumen) {
        pages = decoder.decode(fumen);
        input = pages[0]['_field']['field']['pieces'];

        let board = new Array(17).fill(new Array(10).fill({ t: 0, c: '' })); // empty top 17 rows
        for (rowIndex = 0; rowIndex < 23; rowIndex++) {
            let row = [];
            for (colIndex = 0; colIndex < 10; colIndex++) {
                index = (23 - rowIndex - 1) * 10 + colIndex;
                colorIndex = input[index];
                if (colorIndex == 0) row.push({ t: 0, c: '' });
                else {
                    letter = ' ILOZTJSX'[colorIndex];
                    row.push({ t: 1, c: letter });
                }
            }
            board.push(row);
        }
        return board;
    };

    window.fullDecode = function fullDecode(fumen, oldHist) {
        pages = decoder.decode(fumen);
        newHist = [];
        for (i = 0; i < pages.length; i++) {
            input = pages[i]['_field']['field']['pieces'];
            let tempBoard = new Array(17).fill(new Array(10).fill({ t: 0, c: '' })); // empty top 17 rows
            for (rowIndex = 0; rowIndex < 23; rowIndex++) {
                let row = [];
                for (colIndex = 0; colIndex < 10; colIndex++) {
                    index = (23 - rowIndex - 1) * 10 + colIndex;
                    colorIndex = input[index];
                    if (colorIndex == 0) row.push({ t: 0, c: '' });
                    else {
                        letter = ' ILOZTJSX'[colorIndex];
                        row.push({ t: 1, c: letter });
                    }
                }
                tempBoard.push(row);
            }

            currHist = {
                board: JSON.stringify(tempBoard),
                queue: oldHist['queue'],
                hold: oldHist['hold'],
                piece: oldHist['piece'],
            };

            comment = pages[i]['comment'];

            if (pages[i]['flags']['quiz'] && comment.substring(0, 3) == '#Q=') {
                bracketStart = comment.indexOf('[');
                bracketEnd = comment.indexOf(']');
                if (bracketStart >= 0 && bracketEnd == bracketStart + 2 && 'SZLJIOT'.includes(comment[bracketStart + 1])) {
                    currHist['hold'] = comment[bracketStart + 1];
                } else currHist['hold'] = '';

                bracketStart = comment.indexOf('(');
                bracketEnd = comment.indexOf(')');
                if (bracketStart >= 0 && bracketEnd == bracketStart + 2 && 'SZLJIOT'.includes(comment[bracketStart + 1])) {
                    currHist['piece'] = comment[bracketStart + 1];
                }

                currQueue = comment.substring(bracketEnd + 1);
                temp = [];
                for (j = 0; j < currQueue.length; j++) {
                    //sanitization
                    if ('SZLJIOT'.includes(currQueue[j])) temp.push(currQueue[j]);
                }
                temp.push('|');
                while (temp.length < 10) {
                    var shuf = names.shuffle();
                    shuf.map((p) => temp.push(p));
                    temp.push('|');
                }
                currHist['queue'] = JSON.stringify(temp);

            }

            newHist.push(currHist);
        }
        return newHist;
    };

    window.encode = function encode(board) {
        pages = [];
        pages.push(toPage(board));
        fumen = encoder.encode(pages);
        return fumen;
    };

    window.fullEncode = function fullEncode(hist) {
        pages = [];
        for (let i = 0; i < hist.length; i++) {
            pages.push(toPage(JSON.parse(hist[i]['board'])));
        }
        fumen = encoder.encode(pages);
        return fumen;
    };

    },{"tetris-fumen":2}],2:[function(require,module,exports){
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var decoder_1 = require("./lib/decoder");
    var encoder_1 = require("./lib/encoder");
    var field_1 = require("./lib/field");
    exports.Field = field_1.Field;
    exports.Mino = field_1.Mino;
    exports.decoder = {
        decode: function (data) {
            return decoder_1.decode(data);
        },
    };
    exports.encoder = {
        encode: function (data) {
            return "v115@" + encoder_1.encode(data);
        },
    };

    },{"./lib/decoder":6,"./lib/encoder":8,"./lib/field":9}],3:[function(require,module,exports){
    "use strict";
    var __assign = (this && this.__assign) || function () {
        __assign = Object.assign || function(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                    t[p] = s[p];
            }
            return t;
        };
        return __assign.apply(this, arguments);
    };
    Object.defineProperty(exports, "__esModule", { value: true });
    var defines_1 = require("./defines");
    function decodeBool(n) {
        return n !== 0;
    }
    exports.createActionDecoder = function (width, fieldTop, garbageLine) {
        var fieldMaxHeight = fieldTop + garbageLine;
        var numFieldBlocks = fieldMaxHeight * width;
        function decodePiece(n) {
            switch (n) {
                case 0:
                    return defines_1.Piece.Empty;
                case 1:
                    return defines_1.Piece.I;
                case 2:
                    return defines_1.Piece.L;
                case 3:
                    return defines_1.Piece.O;
                case 4:
                    return defines_1.Piece.Z;
                case 5:
                    return defines_1.Piece.T;
                case 6:
                    return defines_1.Piece.J;
                case 7:
                    return defines_1.Piece.S;
                case 8:
                    return defines_1.Piece.Gray;
            }
            throw new Error('Unexpected piece');
        }
        function decodeRotation(n) {
            switch (n) {
                case 0:
                    return defines_1.Rotation.Reverse;
                case 1:
                    return defines_1.Rotation.Right;
                case 2:
                    return defines_1.Rotation.Spawn;
                case 3:
                    return defines_1.Rotation.Left;
            }
            throw new Error('Unexpected rotation');
        }
        function decodeCoordinate(n, piece, rotation) {
            var x = n % width;
            var originY = Math.floor(n / 10);
            var y = fieldTop - originY - 1;
            if (piece === defines_1.Piece.O && rotation === defines_1.Rotation.Left) {
                x += 1;
                y -= 1;
            }
            else if (piece === defines_1.Piece.O && rotation === defines_1.Rotation.Reverse) {
                x += 1;
            }
            else if (piece === defines_1.Piece.O && rotation === defines_1.Rotation.Spawn) {
                y -= 1;
            }
            else if (piece === defines_1.Piece.I && rotation === defines_1.Rotation.Reverse) {
                x += 1;
            }
            else if (piece === defines_1.Piece.I && rotation === defines_1.Rotation.Left) {
                y -= 1;
            }
            else if (piece === defines_1.Piece.S && rotation === defines_1.Rotation.Spawn) {
                y -= 1;
            }
            else if (piece === defines_1.Piece.S && rotation === defines_1.Rotation.Right) {
                x -= 1;
            }
            else if (piece === defines_1.Piece.Z && rotation === defines_1.Rotation.Spawn) {
                y -= 1;
            }
            else if (piece === defines_1.Piece.Z && rotation === defines_1.Rotation.Left) {
                x += 1;
            }
            return { x: x, y: y };
        }
        return {
            decode: function (v) {
                var value = v;
                var type = decodePiece(value % 8);
                value = Math.floor(value / 8);
                var rotation = decodeRotation(value % 4);
                value = Math.floor(value / 4);
                var coordinate = decodeCoordinate(value % numFieldBlocks, type, rotation);
                value = Math.floor(value / numFieldBlocks);
                var isBlockUp = decodeBool(value % 2);
                value = Math.floor(value / 2);
                var isMirror = decodeBool(value % 2);
                value = Math.floor(value / 2);
                var isColor = decodeBool(value % 2);
                value = Math.floor(value / 2);
                var isComment = decodeBool(value % 2);
                value = Math.floor(value / 2);
                var isLock = !decodeBool(value % 2);
                return {
                    rise: isBlockUp,
                    mirror: isMirror,
                    colorize: isColor,
                    comment: isComment,
                    lock: isLock,
                    piece: __assign(__assign({}, coordinate), { type: type,
                        rotation: rotation }),
                };
            },
        };
    };
    function encodeBool(flag) {
        return flag ? 1 : 0;
    }
    exports.createActionEncoder = function (width, fieldTop, garbageLine) {
        var fieldMaxHeight = fieldTop + garbageLine;
        var numFieldBlocks = fieldMaxHeight * width;
        function encodePosition(operation) {
            var type = operation.type, rotation = operation.rotation;
            var x = operation.x;
            var y = operation.y;
            if (!defines_1.isMinoPiece(type)) {
                x = 0;
                y = 22;
            }
            else if (type === defines_1.Piece.O && rotation === defines_1.Rotation.Left) {
                x -= 1;
                y += 1;
            }
            else if (type === defines_1.Piece.O && rotation === defines_1.Rotation.Reverse) {
                x -= 1;
            }
            else if (type === defines_1.Piece.O && rotation === defines_1.Rotation.Spawn) {
                y += 1;
            }
            else if (type === defines_1.Piece.I && rotation === defines_1.Rotation.Reverse) {
                x -= 1;
            }
            else if (type === defines_1.Piece.I && rotation === defines_1.Rotation.Left) {
                y += 1;
            }
            else if (type === defines_1.Piece.S && rotation === defines_1.Rotation.Spawn) {
                y += 1;
            }
            else if (type === defines_1.Piece.S && rotation === defines_1.Rotation.Right) {
                x += 1;
            }
            else if (type === defines_1.Piece.Z && rotation === defines_1.Rotation.Spawn) {
                y += 1;
            }
            else if (type === defines_1.Piece.Z && rotation === defines_1.Rotation.Left) {
                x -= 1;
            }
            return (fieldTop - y - 1) * width + x;
        }
        function encodeRotation(_a) {
            var type = _a.type, rotation = _a.rotation;
            if (!defines_1.isMinoPiece(type)) {
                return 0;
            }
            switch (rotation) {
                case defines_1.Rotation.Reverse:
                    return 0;
                case defines_1.Rotation.Right:
                    return 1;
                case defines_1.Rotation.Spawn:
                    return 2;
                case defines_1.Rotation.Left:
                    return 3;
            }
            throw new Error('No reachable');
        }
        return {
            encode: function (action) {
                var lock = action.lock, comment = action.comment, colorize = action.colorize, mirror = action.mirror, rise = action.rise, piece = action.piece;
                var value = encodeBool(!lock);
                value *= 2;
                value += encodeBool(comment);
                value *= 2;
                value += (encodeBool(colorize));
                value *= 2;
                value += encodeBool(mirror);
                value *= 2;
                value += encodeBool(rise);
                value *= numFieldBlocks;
                value += encodePosition(piece);
                value *= 4;
                value += encodeRotation(piece);
                value *= 8;
                value += piece.type;
                return value;
            },
        };
    };

    },{"./defines":7}],4:[function(require,module,exports){
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var ENCODE_TABLE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    var Buffer = /** @class */ (function () {
        function Buffer(data) {
            if (data === void 0) { data = ''; }
            this.values = data.split('').map(decodeToValue);
        }
        Buffer.prototype.poll = function (max) {
            var value = 0;
            for (var count = 0; count < max; count += 1) {
                var v = this.values.shift();
                if (v === undefined) {
                    throw new Error('Unexpected fumen');
                }
                value += v * Math.pow(Buffer.tableLength, count);
            }
            return value;
        };
        Buffer.prototype.push = function (value, splitCount) {
            if (splitCount === void 0) { splitCount = 1; }
            var current = value;
            for (var count = 0; count < splitCount; count += 1) {
                this.values.push(current % Buffer.tableLength);
                current = Math.floor(current / Buffer.tableLength);
            }
        };
        Buffer.prototype.merge = function (postBuffer) {
            for (var _i = 0, _a = postBuffer.values; _i < _a.length; _i++) {
                var value = _a[_i];
                this.values.push(value);
            }
        };
        Buffer.prototype.isEmpty = function () {
            return this.values.length === 0;
        };
        Object.defineProperty(Buffer.prototype, "length", {
            get: function () {
                return this.values.length;
            },
            enumerable: true,
            configurable: true
        });
        Buffer.prototype.get = function (index) {
            return this.values[index];
        };
        Buffer.prototype.set = function (index, value) {
            this.values[index] = value;
        };
        Buffer.prototype.toString = function () {
            return this.values.map(encodeFromValue).join('');
        };
        Buffer.tableLength = ENCODE_TABLE.length;
        return Buffer;
    }());
    exports.Buffer = Buffer;
    function decodeToValue(v) {
        return ENCODE_TABLE.indexOf(v);
    }
    function encodeFromValue(index) {
        return ENCODE_TABLE[index];
    }

    },{}],5:[function(require,module,exports){
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var COMMENT_TABLE = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~';
    var MAX_COMMENT_CHAR_VALUE = COMMENT_TABLE.length + 1;
    exports.createCommentParser = function () {
        return {
            decode: function (v) {
                var str = '';
                var value = v;
                for (var count = 0; count < 4; count += 1) {
                    var index = value % MAX_COMMENT_CHAR_VALUE;
                    str += COMMENT_TABLE[index];
                    value = Math.floor(value / MAX_COMMENT_CHAR_VALUE);
                }
                return str;
            },
            encode: function (ch, count) {
                return COMMENT_TABLE.indexOf(ch) * Math.pow(MAX_COMMENT_CHAR_VALUE, count);
            },
        };
    };

    },{}],6:[function(require,module,exports){
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var inner_field_1 = require("./inner_field");
    var buffer_1 = require("./buffer");
    var defines_1 = require("./defines");
    var action_1 = require("./action");
    var comments_1 = require("./comments");
    var quiz_1 = require("./quiz");
    var field_1 = require("./field");
    var Page = /** @class */ (function () {
        function Page(index, field, operation, comment, flags, refs) {
            this.index = index;
            this.operation = operation;
            this.comment = comment;
            this.flags = flags;
            this.refs = refs;
            this._field = field.copy();
        }
        Object.defineProperty(Page.prototype, "field", {
            get: function () {
                return new field_1.Field(this._field.copy());
            },
            set: function (field) {
                this._field = inner_field_1.createInnerField(field);
            },
            enumerable: true,
            configurable: true
        });
        Page.prototype.mino = function () {
            return field_1.Mino.from(this.operation);
        };
        return Page;
    }());
    exports.Page = Page;
    var FieldConstants = {
        GarbageLine: 1,
        Width: 10,
    };
    function extract(str) {
        var format = function (version, data) {
            var trim = data.trim().replace(/[?\s]+/g, '');
            return { version: version, data: trim };
        };
        var data = str;
        // url parameters
        var paramIndex = data.indexOf('&');
        if (0 <= paramIndex) {
            data = data.substring(0, paramIndex);
        }
        // v115@~
        {
            var match = str.match(/[vmd]115@/);
            if (match !== undefined && match !== null && match.index !== undefined) {
                var sub = data.substr(match.index + 5);
                return format('115', sub);
            }
        }
        // v110@~
        {
            var match = str.match(/[vmd]110@/);
            if (match !== undefined && match !== null && match.index !== undefined) {
                var sub = data.substr(match.index + 5);
                return format('110', sub);
            }
        }
        throw new Error('Unsupported fumen version');
    }
    exports.extract = extract;
    function decode(fumen) {
        var _a = extract(fumen), version = _a.version, data = _a.data;
        switch (version) {
            case '115':
                return innerDecode(data, 23);
            case '110':
                return innerDecode(data, 21);
        }
        throw new Error('Unsupported fumen version');
    }
    exports.decode = decode;
    function innerDecode(data, fieldTop) {
        var fieldMaxHeight = fieldTop + FieldConstants.GarbageLine;
        var numFieldBlocks = fieldMaxHeight * FieldConstants.Width;
        var buffer = new buffer_1.Buffer(data);
        var updateField = function (prev) {
            var result = {
                changed: false,
                field: prev,
            };
            var index = 0;
            while (index < numFieldBlocks) {
                var diffBlock = buffer.poll(2);
                var diff = Math.floor(diffBlock / numFieldBlocks);
                var numOfBlocks = diffBlock % numFieldBlocks;
                if (numOfBlocks !== numFieldBlocks - 1) {
                    result.changed = true;
                }
                for (var block = 0; block < numOfBlocks + 1; block += 1) {
                    var x = index % FieldConstants.Width;
                    var y = fieldTop - Math.floor(index / FieldConstants.Width) - 1;
                    result.field.addNumber(x, y, diff - 8);
                    index += 1;
                }
            }
            return result;
        };
        var pageIndex = 0;
        var prevField = inner_field_1.createNewInnerField();
        var store = {
            repeatCount: -1,
            refIndex: {
                comment: 0,
                field: 0,
            },
            quiz: undefined,
            lastCommentText: '',
        };
        var pages = [];
        var actionDecoder = action_1.createActionDecoder(FieldConstants.Width, fieldTop, FieldConstants.GarbageLine);
        var commentDecoder = comments_1.createCommentParser();
        while (!buffer.isEmpty()) {
            // Parse field
            var currentFieldObj = void 0;
            if (0 < store.repeatCount) {
                currentFieldObj = {
                    field: prevField,
                    changed: false,
                };
                store.repeatCount -= 1;
            }
            else {
                currentFieldObj = updateField(prevField.copy());
                if (!currentFieldObj.changed) {
                    store.repeatCount = buffer.poll(1);
                }
            }
            // Parse action
            var actionValue = buffer.poll(3);
            var action = actionDecoder.decode(actionValue);
            // Parse comment
            var comment = void 0;
            if (action.comment) {
                // πé│πâíπâ│πâêπü½µ¢┤µû░πüîπüéπéïπü¿πüì
                var commentValues = [];
                var commentLength = buffer.poll(2);
                for (var commentCounter = 0; commentCounter < Math.floor((commentLength + 3) / 4); commentCounter += 1) {
                    var commentValue = buffer.poll(5);
                    commentValues.push(commentValue);
                }
                var flatten = '';
                for (var _i = 0, commentValues_1 = commentValues; _i < commentValues_1.length; _i++) {
                    var value = commentValues_1[_i];
                    flatten += commentDecoder.decode(value);
                }
                var commentText = unescape(flatten.slice(0, commentLength));
                store.lastCommentText = commentText;
                comment = { text: commentText };
                store.refIndex.comment = pageIndex;
                var text = comment.text;
                if (quiz_1.Quiz.isQuizComment(text)) {
                    try {
                        store.quiz = new quiz_1.Quiz(text);
                    }
                    catch (e) {
                        store.quiz = undefined;
                    }
                }
                else {
                    store.quiz = undefined;
                }
            }
            else if (pageIndex === 0) {
                // πé│πâíπâ│πâêπü½µ¢┤µû░πüîπü¬πüäπüîπÇüσàêΘá¡πü«πâÜπâ╝πé╕πü«πü¿πüì
                comment = { text: '' };
            }
            else {
                // πé│πâíπâ│πâêπü½µ¢┤µû░πüîπü¬πüäπü¿πüì
                comment = {
                    text: store.quiz !== undefined ? store.quiz.format().toString() : undefined,
                    ref: store.refIndex.comment,
                };
            }
            // Quizτö¿πü«µôìΣ╜£πéÆσÅûσ╛ùπüùπÇüµ¼íπâÜπâ╝πé╕ΘûïσºïµÖéτé╣πü«Quizπü½1µëïΘÇ▓πéüπéï
            var quiz = false;
            if (store.quiz !== undefined) {
                quiz = true;
                if (store.quiz.canOperate() && action.lock) {
                    if (defines_1.isMinoPiece(action.piece.type)) {
                        try {
                            var nextQuiz = store.quiz.nextIfEnd();
                            var operation = nextQuiz.getOperation(action.piece.type);
                            store.quiz = nextQuiz.operate(operation);
                        }
                        catch (e) {
                            // console.error(e.message);
                            // Not operate
                            store.quiz = store.quiz.format();
                        }
                    }
                    else {
                        store.quiz = store.quiz.format();
                    }
                }
            }
            // πâçπâ╝πé┐σçªτÉåτö¿πü½σèáσ╖ÑπüÖπéï
            var currentPiece = void 0;
            if (action.piece.type !== defines_1.Piece.Empty) {
                currentPiece = action.piece;
            }
            // pageπü«Σ╜£µêÉ
            var field = void 0;
            if (currentFieldObj.changed || pageIndex === 0) {
                // πâòπéúπâ╝πâ½πâëπü½σñëσîûπüîπüéπüúπüƒπü¿πüì
                // πâòπéúπâ╝πâ½πâëπü½σñëσîûπüîπü¬πüïπüúπüƒπüîπÇüσàêΘá¡πü«πâÜπâ╝πé╕πüáπüúπüƒπü¿πüì
                field = {};
                store.refIndex.field = pageIndex;
            }
            else {
                // πâòπéúπâ╝πâ½πâëπü½σñëσîûπüîπü¬πüäπü¿πüì
                field = { ref: store.refIndex.field };
            }
            pages.push(new Page(pageIndex, currentFieldObj.field, currentPiece !== undefined ? field_1.Mino.from({
                type: defines_1.parsePieceName(currentPiece.type),
                rotation: defines_1.parseRotationName(currentPiece.rotation),
                x: currentPiece.x,
                y: currentPiece.y,
            }) : undefined, comment.text !== undefined ? comment.text : store.lastCommentText, {
                quiz: quiz,
                lock: action.lock,
                mirror: action.mirror,
                colorize: action.colorize,
                rise: action.rise,
            }, {
                field: field.ref,
                comment: comment.ref,
            }));
            // callback(
            //     currentFieldObj.field.copy()
            //     , currentPiece
            //     , store.quiz !== undefined ? store.quiz.format().toString() : store.lastCommentText,
            // );
            pageIndex += 1;
            if (action.lock) {
                if (defines_1.isMinoPiece(action.piece.type)) {
                    currentFieldObj.field.fill(action.piece);
                }
                currentFieldObj.field.clearLine();
                if (action.rise) {
                    currentFieldObj.field.riseGarbage();
                }
                if (action.mirror) {
                    currentFieldObj.field.mirror();
                }
            }
            prevField = currentFieldObj.field;
        }
        return pages;
    }

    },{"./action":3,"./buffer":4,"./comments":5,"./defines":7,"./field":9,"./inner_field":10,"./quiz":11}],7:[function(require,module,exports){
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var Piece;
    (function (Piece) {
        Piece[Piece["Empty"] = 0] = "Empty";
        Piece[Piece["I"] = 1] = "I";
        Piece[Piece["L"] = 2] = "L";
        Piece[Piece["O"] = 3] = "O";
        Piece[Piece["Z"] = 4] = "Z";
        Piece[Piece["T"] = 5] = "T";
        Piece[Piece["J"] = 6] = "J";
        Piece[Piece["S"] = 7] = "S";
        Piece[Piece["Gray"] = 8] = "Gray";
    })(Piece = exports.Piece || (exports.Piece = {}));
    function isMinoPiece(piece) {
        return piece !== Piece.Empty && piece !== Piece.Gray;
    }
    exports.isMinoPiece = isMinoPiece;
    function parsePieceName(piece) {
        switch (piece) {
            case Piece.I:
                return 'I';
            case Piece.L:
                return 'L';
            case Piece.O:
                return 'O';
            case Piece.Z:
                return 'Z';
            case Piece.T:
                return 'T';
            case Piece.J:
                return 'J';
            case Piece.S:
                return 'S';
            case Piece.Gray:
                return 'X';
            case Piece.Empty:
                return '_';
        }
        throw new Error("Unknown piece: " + piece);
    }
    exports.parsePieceName = parsePieceName;
    function parsePiece(piece) {
        switch (piece.toUpperCase()) {
            case 'I':
                return Piece.I;
            case 'L':
                return Piece.L;
            case 'O':
                return Piece.O;
            case 'Z':
                return Piece.Z;
            case 'T':
                return Piece.T;
            case 'J':
                return Piece.J;
            case 'S':
                return Piece.S;
            case 'X':
            case 'GRAY':
                return Piece.Gray;
            case ' ':
            case '_':
            case 'EMPTY':
                return Piece.Empty;
        }
        throw new Error("Unknown piece: " + piece);
    }
    exports.parsePiece = parsePiece;
    var Rotation;
    (function (Rotation) {
        Rotation[Rotation["Spawn"] = 0] = "Spawn";
        Rotation[Rotation["Right"] = 1] = "Right";
        Rotation[Rotation["Reverse"] = 2] = "Reverse";
        Rotation[Rotation["Left"] = 3] = "Left";
    })(Rotation = exports.Rotation || (exports.Rotation = {}));
    function parseRotationName(rotation) {
        switch (rotation) {
            case Rotation.Spawn:
                return 'spawn';
            case Rotation.Left:
                return 'left';
            case Rotation.Right:
                return 'right';
            case Rotation.Reverse:
                return 'reverse';
        }
        throw new Error("Unknown rotation: " + rotation);
    }
    exports.parseRotationName = parseRotationName;
    function parseRotation(rotation) {
        switch (rotation.toLowerCase()) {
            case 'spawn':
                return Rotation.Spawn;
            case 'left':
                return Rotation.Left;
            case 'right':
                return Rotation.Right;
            case 'reverse':
                return Rotation.Reverse;
        }
        throw new Error("Unknown rotation: " + rotation);
    }
    exports.parseRotation = parseRotation;

    },{}],8:[function(require,module,exports){
    "use strict";
    var __assign = (this && this.__assign) || function () {
        __assign = Object.assign || function(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                    t[p] = s[p];
            }
            return t;
        };
        return __assign.apply(this, arguments);
    };
    Object.defineProperty(exports, "__esModule", { value: true });
    var inner_field_1 = require("./inner_field");
    var buffer_1 = require("./buffer");
    var defines_1 = require("./defines");
    var action_1 = require("./action");
    var comments_1 = require("./comments");
    var quiz_1 = require("./quiz");
    var FieldConstants = {
        GarbageLine: 1,
        Width: 10,
    };
    function encode(pages) {
        var updateField = function (prev, current) {
            var _a = encodeField(prev, current), changed = _a.changed, values = _a.values;
            if (changed) {
                // πâòπéúπâ╝πâ½πâëπéÆΦ¿ÿΘî▓πüùπüªπÇüπâ¬πâöπâ╝πâêπéÆτ╡éΣ║åπüÖπéï
                buffer.merge(values);
                lastRepeatIndex = -1;
            }
            else if (lastRepeatIndex < 0 || buffer.get(lastRepeatIndex) === buffer_1.Buffer.tableLength - 1) {
                // πâòπéúπâ╝πâ½πâëπéÆΦ¿ÿΘî▓πüùπüªπÇüπâ¬πâöπâ╝πâêπéÆΘûïσºïπüÖπéï
                buffer.merge(values);
                buffer.push(0);
                lastRepeatIndex = buffer.length - 1;
            }
            else if (buffer.get(lastRepeatIndex) < (buffer_1.Buffer.tableLength - 1)) {
                // πâòπéúπâ╝πâ½πâëπü»Φ¿ÿΘî▓πü¢πüÜπÇüπâ¬πâöπâ╝πâêπéÆΘÇ▓πéüπéï
                var currentRepeatValue = buffer.get(lastRepeatIndex);
                buffer.set(lastRepeatIndex, currentRepeatValue + 1);
            }
        };
        var lastRepeatIndex = -1;
        var buffer = new buffer_1.Buffer();
        var prevField = inner_field_1.createNewInnerField();
        var actionEncoder = action_1.createActionEncoder(FieldConstants.Width, 23, FieldConstants.GarbageLine);
        var commentParser = comments_1.createCommentParser();
        var prevComment = '';
        var prevQuiz = undefined;
        var innerEncode = function (index) {
            var currentPage = pages[index];
            var field = currentPage.field;
            var currentField = field !== undefined ? inner_field_1.createInnerField(field) : prevField.copy();
            // πâòπéúπâ╝πâ½πâëπü«µ¢┤µû░
            updateField(prevField, currentField);
            // πéóπé»πé╖πâºπâ│πü«µ¢┤µû░
            var currentComment = currentPage.comment !== undefined
                ? ((index !== 0 || currentPage.comment !== '') ? currentPage.comment : undefined)
                : undefined;
            var piece = currentPage.operation !== undefined ? {
                type: defines_1.parsePiece(currentPage.operation.type),
                rotation: defines_1.parseRotation(currentPage.operation.rotation),
                x: currentPage.operation.x,
                y: currentPage.operation.y,
            } : {
                type: defines_1.Piece.Empty,
                rotation: defines_1.Rotation.Reverse,
                x: 0,
                y: 22,
            };
            var nextComment;
            if (currentComment !== undefined) {
                if (currentComment.startsWith('#Q=')) {
                    // Quiz on
                    if (prevQuiz !== undefined && prevQuiz.format().toString() === currentComment) {
                        nextComment = undefined;
                    }
                    else {
                        nextComment = currentComment;
                        prevComment = nextComment;
                        prevQuiz = new quiz_1.Quiz(currentComment);
                    }
                }
                else {
                    // Quiz off
                    if (prevQuiz !== undefined && prevQuiz.format().toString() === currentComment) {
                        nextComment = undefined;
                        prevComment = currentComment;
                        prevQuiz = undefined;
                    }
                    else {
                        nextComment = prevComment !== currentComment ? currentComment : undefined;
                        prevComment = prevComment !== currentComment ? nextComment : prevComment;
                        prevQuiz = undefined;
                    }
                }
            }
            else {
                nextComment = undefined;
                prevQuiz = undefined;
            }
            if (prevQuiz !== undefined && prevQuiz.canOperate() && currentPage.flags.lock) {
                if (defines_1.isMinoPiece(piece.type)) {
                    try {
                        var nextQuiz = prevQuiz.nextIfEnd();
                        var operation = nextQuiz.getOperation(piece.type);
                        prevQuiz = nextQuiz.operate(operation);
                    }
                    catch (e) {
                        // console.error(e.message);
                        // Not operate
                        prevQuiz = prevQuiz.format();
                    }
                }
                else {
                    prevQuiz = prevQuiz.format();
                }
            }
            var currentFlags = __assign({ lock: true, colorize: index === 0 }, currentPage.flags);
            var action = {
                piece: piece,
                rise: !!currentFlags.rise,
                mirror: !!currentFlags.mirror,
                colorize: !!currentFlags.colorize,
                lock: !!currentFlags.lock,
                comment: nextComment !== undefined,
            };
            var actionNumber = actionEncoder.encode(action);
            buffer.push(actionNumber, 3);
            // πé│πâíπâ│πâêπü«µ¢┤µû░
            if (nextComment !== undefined) {
                var comment = escape(currentPage.comment);
                var commentLength = Math.min(comment.length, 4095);
                buffer.push(commentLength, 2);
                // πé│πâíπâ│πâêπéÆτ¼ªσÅ╖σîû
                for (var index_1 = 0; index_1 < commentLength; index_1 += 4) {
                    var value = 0;
                    for (var count = 0; count < 4; count += 1) {
                        var newIndex = index_1 + count;
                        if (commentLength <= newIndex) {
                            break;
                        }
                        var ch = comment.charAt(newIndex);
                        value += commentParser.encode(ch, count);
                    }
                    buffer.push(value, 5);
                }
            }
            else if (currentPage.comment === undefined) {
                prevComment = undefined;
            }
            // σ£░σ╜óπü«µ¢┤µû░
            if (action.lock) {
                if (defines_1.isMinoPiece(action.piece.type)) {
                    currentField.fill(action.piece);
                }
                currentField.clearLine();
                if (action.rise) {
                    currentField.riseGarbage();
                }
                if (action.mirror) {
                    currentField.mirror();
                }
            }
            prevField = currentField;
        };
        for (var index = 0; index < pages.length; index += 1) {
            innerEncode(index);
        }
        // πâåπâêΦ¡£πüîτƒ¡πüäπü¿πüìπü»πü¥πü«πü╛πü╛σç║σè¢πüÖπéï
        // 47µûçσ¡ùπüöπü¿πü½?πüîµî┐σàÑπüòπéîπéïπüîπÇüσ«ƒΘÜ¢πü»σàêΘá¡πü½v115@πüîσàÑπéïπüƒπéüπÇüµ£Çσê¥πü«?πü»42µûçσ¡ùσ╛îπü½πü¬πéï
        var data = buffer.toString();
        if (data.length < 41) {
            return data;
        }
        // ?πéÆµî┐σàÑπüÖπéï
        var head = [data.substr(0, 42)];
        var tails = data.substring(42);
        var split = tails.match(/[\S]{1,47}/g) || [];
        return head.concat(split).join('?');
    }
    exports.encode = encode;
    // πâòπéúπâ╝πâ½πâëπéÆπé¿πâ│πé│πâ╝πâëπüÖπéï
    // σëìπü«πâòπéúπâ╝πâ½πâëπüîπü¬πüäπü¿πüìπü»τ⌐║πü«πâòπéúπâ╝πâ½πâëπéÆµîçσ«ÜπüÖπéï
    // σàÑσè¢πâòπéúπâ╝πâ½πâëπü«Θ½ÿπüòπü»23, σ╣àπü»10
    function encodeField(prev, current) {
        var FIELD_TOP = 23;
        var FIELD_MAX_HEIGHT = FIELD_TOP + 1;
        var FIELD_BLOCKS = FIELD_MAX_HEIGHT * FieldConstants.Width;
        var buffer = new buffer_1.Buffer();
        // σëìπü«πâòπéúπâ╝πâ½πâëπü¿πü«σ╖«πéÆΦ¿êτ«ù: 0πÇ£16
        var getDiff = function (xIndex, yIndex) {
            var y = FIELD_TOP - yIndex - 1;
            return current.getNumberAt(xIndex, y) - prev.getNumberAt(xIndex, y) + 8;
        };
        // πâçπâ╝πé┐πü«Φ¿ÿΘî▓
        var recordBlockCounts = function (diff, counter) {
            var value = diff * FIELD_BLOCKS + counter;
            buffer.push(value, 2);
        };
        // πâòπéúπâ╝πâ½πâëσÇñπüïπéëΘÇúτ╢Üπüùπüƒπâûπâ¡πââπé»µò░πü½σñëµÅ¢
        var changed = false;
        var prev_diff = getDiff(0, 0);
        var counter = -1;
        for (var yIndex = 0; yIndex < FIELD_MAX_HEIGHT; yIndex += 1) {
            for (var xIndex = 0; xIndex < FieldConstants.Width; xIndex += 1) {
                var diff = getDiff(xIndex, yIndex);
                if (diff !== prev_diff) {
                    recordBlockCounts(prev_diff, counter);
                    counter = 0;
                    prev_diff = diff;
                    changed = true;
                }
                else {
                    counter += 1;
                }
            }
        }
        // µ£Çσ╛îπü«ΘÇúτ╢Üπâûπâ¡πââπé»πéÆσçªτÉå
        recordBlockCounts(prev_diff, counter);
        return {
            changed: changed,
            values: buffer,
        };
    }

    },{"./action":3,"./buffer":4,"./comments":5,"./defines":7,"./inner_field":10,"./quiz":11}],9:[function(require,module,exports){
    "use strict";
    var __assign = (this && this.__assign) || function () {
        __assign = Object.assign || function(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                    t[p] = s[p];
            }
            return t;
        };
        return __assign.apply(this, arguments);
    };
    Object.defineProperty(exports, "__esModule", { value: true });
    var inner_field_1 = require("./inner_field");
    var defines_1 = require("./defines");
    function toMino(operationOrMino) {
        return operationOrMino instanceof Mino ? operationOrMino.copy() : Mino.from(operationOrMino);
    }
    var Field = /** @class */ (function () {
        function Field(field) {
            this.field = field;
        }
        Field.create = function (field, garbage) {
            return new Field(new inner_field_1.InnerField({
                field: field !== undefined ? inner_field_1.PlayField.load(field) : undefined,
                garbage: garbage !== undefined ? inner_field_1.PlayField.loadMinify(garbage) : undefined,
            }));
        };
        Field.prototype.canFill = function (operation) {
            if (operation === undefined) {
                return true;
            }
            var mino = toMino(operation);
            return this.field.canFillAll(mino.positions());
        };
        Field.prototype.canLock = function (operation) {
            if (operation === undefined) {
                return true;
            }
            if (!this.canFill(operation)) {
                return false;
            }
            // Check on the ground
            return !this.canFill(__assign(__assign({}, operation), { y: operation.y - 1 }));
        };
        Field.prototype.fill = function (operation, force) {
            if (force === void 0) { force = false; }
            if (operation === undefined) {
                return undefined;
            }
            var mino = toMino(operation);
            if (!force && !this.canFill(mino)) {
                throw Error('Cannot fill piece on field');
            }
            this.field.fillAll(mino.positions(), defines_1.parsePiece(mino.type));
            return mino;
        };
        Field.prototype.put = function (operation) {
            if (operation === undefined) {
                return undefined;
            }
            var mino = toMino(operation);
            for (; 0 <= mino.y; mino.y -= 1) {
                if (!this.canLock(mino)) {
                    continue;
                }
                this.fill(mino);
                return mino;
            }
            throw Error('Cannot put piece on field');
        };
        Field.prototype.clearLine = function () {
            this.field.clearLine();
        };
        Field.prototype.at = function (x, y) {
            return defines_1.parsePieceName(this.field.getNumberAt(x, y));
        };
        Field.prototype.set = function (x, y, type) {
            this.field.setNumberAt(x, y, defines_1.parsePiece(type));
        };
        Field.prototype.copy = function () {
            return new Field(this.field.copy());
        };
        Field.prototype.str = function (option) {
            if (option === void 0) { option = {}; }
            var skip = option.reduced !== undefined ? option.reduced : true;
            var separator = option.separator !== undefined ? option.separator : '\n';
            var minY = option.garbage === undefined || option.garbage ? -1 : 0;
            var output = '';
            for (var y = 22; minY <= y; y -= 1) {
                var line = '';
                for (var x = 0; x < 10; x += 1) {
                    line += this.at(x, y);
                }
                if (skip && line === '__________') {
                    continue;
                }
                skip = false;
                output += line;
                if (y !== minY) {
                    output += separator;
                }
            }
            return output;
        };
        return Field;
    }());
    exports.Field = Field;
    var Mino = /** @class */ (function () {
        function Mino(type, rotation, x, y) {
            this.type = type;
            this.rotation = rotation;
            this.x = x;
            this.y = y;
        }
        Mino.from = function (operation) {
            return new Mino(operation.type, operation.rotation, operation.x, operation.y);
        };
        Mino.prototype.positions = function () {
            return inner_field_1.getBlockXYs(defines_1.parsePiece(this.type), defines_1.parseRotation(this.rotation), this.x, this.y).sort(function (a, b) {
                if (a.y === b.y) {
                    return a.x - b.x;
                }
                return a.y - b.y;
            });
        };
        Mino.prototype.operation = function () {
            return {
                type: this.type,
                rotation: this.rotation,
                x: this.x,
                y: this.y,
            };
        };
        Mino.prototype.isValid = function () {
            try {
                defines_1.parsePiece(this.type);
                defines_1.parseRotation(this.rotation);
            }
            catch (e) {
                return false;
            }
            return this.positions().every(function (_a) {
                var x = _a.x, y = _a.y;
                return 0 <= x && x < 10 && 0 <= y && y < 23;
            });
        };
        Mino.prototype.copy = function () {
            return new Mino(this.type, this.rotation, this.x, this.y);
        };
        return Mino;
    }());
    exports.Mino = Mino;

    },{"./defines":7,"./inner_field":10}],10:[function(require,module,exports){
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var defines_1 = require("./defines");
    var FieldConstants = {
        Width: 10,
        Height: 23,
        PlayBlocks: 23 * 10,
    };
    function createNewInnerField() {
        return new InnerField({});
    }
    exports.createNewInnerField = createNewInnerField;
    function createInnerField(field) {
        var innerField = new InnerField({});
        for (var y = -1; y < FieldConstants.Height; y += 1) {
            for (var x = 0; x < FieldConstants.Width; x += 1) {
                var at = field.at(x, y);
                innerField.setNumberAt(x, y, defines_1.parsePiece(at));
            }
        }
        return innerField;
    }
    exports.createInnerField = createInnerField;
    var InnerField = /** @class */ (function () {
        function InnerField(_a) {
            var _b = _a.field, field = _b === void 0 ? InnerField.create(FieldConstants.PlayBlocks) : _b, _c = _a.garbage, garbage = _c === void 0 ? InnerField.create(FieldConstants.Width) : _c;
            this.field = field;
            this.garbage = garbage;
        }
        InnerField.create = function (length) {
            return new PlayField({ length: length });
        };
        InnerField.prototype.fill = function (operation) {
            this.field.fill(operation);
        };
        InnerField.prototype.fillAll = function (positions, type) {
            this.field.fillAll(positions, type);
        };
        InnerField.prototype.canFill = function (piece, rotation, x, y) {
            var _this = this;
            var positions = getBlockPositions(piece, rotation, x, y);
            return positions.every(function (_a) {
                var px = _a[0], py = _a[1];
                return 0 <= px && px < 10
                    && 0 <= py && py < FieldConstants.Height
                    && _this.getNumberAt(px, py) === defines_1.Piece.Empty;
            });
        };
        InnerField.prototype.canFillAll = function (positions) {
            var _this = this;
            return positions.every(function (_a) {
                var x = _a.x, y = _a.y;
                return 0 <= x && x < 10
                    && 0 <= y && y < FieldConstants.Height
                    && _this.getNumberAt(x, y) === defines_1.Piece.Empty;
            });
        };
        InnerField.prototype.isOnGround = function (piece, rotation, x, y) {
            return !this.canFill(piece, rotation, x, y - 1);
        };
        InnerField.prototype.clearLine = function () {
            this.field.clearLine();
        };
        InnerField.prototype.riseGarbage = function () {
            this.field.up(this.garbage);
            this.garbage.clearAll();
        };
        InnerField.prototype.mirror = function () {
            this.field.mirror();
        };
        InnerField.prototype.shiftToLeft = function () {
            this.field.shiftToLeft();
        };
        InnerField.prototype.shiftToRight = function () {
            this.field.shiftToRight();
        };
        InnerField.prototype.shiftToUp = function () {
            this.field.shiftToUp();
        };
        InnerField.prototype.shiftToBottom = function () {
            this.field.shiftToBottom();
        };
        InnerField.prototype.copy = function () {
            return new InnerField({ field: this.field.copy(), garbage: this.garbage.copy() });
        };
        InnerField.prototype.equals = function (other) {
            return this.field.equals(other.field) && this.garbage.equals(other.garbage);
        };
        InnerField.prototype.addNumber = function (x, y, value) {
            if (0 <= y) {
                this.field.addOffset(x, y, value);
            }
            else {
                this.garbage.addOffset(x, -(y + 1), value);
            }
        };
        InnerField.prototype.setNumberFieldAt = function (index, value) {
            this.field.setAt(index, value);
        };
        InnerField.prototype.setNumberGarbageAt = function (index, value) {
            this.garbage.setAt(index, value);
        };
        InnerField.prototype.setNumberAt = function (x, y, value) {
            return 0 <= y ? this.field.set(x, y, value) : this.garbage.set(x, -(y + 1), value);
        };
        InnerField.prototype.getNumberAt = function (x, y) {
            return 0 <= y ? this.field.get(x, y) : this.garbage.get(x, -(y + 1));
        };
        InnerField.prototype.getNumberAtIndex = function (index, isField) {
            if (isField) {
                return this.getNumberAt(index % 10, Math.floor(index / 10));
            }
            return this.getNumberAt(index % 10, -(Math.floor(index / 10) + 1));
        };
        InnerField.prototype.toFieldNumberArray = function () {
            return this.field.toArray();
        };
        InnerField.prototype.toGarbageNumberArray = function () {
            return this.garbage.toArray();
        };
        return InnerField;
    }());
    exports.InnerField = InnerField;
    var PlayField = /** @class */ (function () {
        function PlayField(_a) {
            var pieces = _a.pieces, _b = _a.length, length = _b === void 0 ? FieldConstants.PlayBlocks : _b;
            if (pieces !== undefined) {
                this.pieces = pieces;
            }
            else {
                this.pieces = Array.from({ length: length }).map(function () { return defines_1.Piece.Empty; });
            }
            this.length = length;
        }
        PlayField.load = function () {
            var lines = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                lines[_i] = arguments[_i];
            }
            var blocks = lines.join('').trim();
            return PlayField.loadInner(blocks);
        };
        PlayField.loadMinify = function () {
            var lines = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                lines[_i] = arguments[_i];
            }
            var blocks = lines.join('').trim();
            return PlayField.loadInner(blocks, blocks.length);
        };
        PlayField.loadInner = function (blocks, length) {
            var len = length !== undefined ? length : blocks.length;
            if (len % 10 !== 0) {
                throw new Error('Num of blocks in field should be mod 10');
            }
            var field = length !== undefined ? new PlayField({ length: length }) : new PlayField({});
            for (var index = 0; index < len; index += 1) {
                var block = blocks[index];
                field.set(index % 10, Math.floor((len - index - 1) / 10), defines_1.parsePiece(block));
            }
            return field;
        };
        PlayField.prototype.get = function (x, y) {
            return this.pieces[x + y * FieldConstants.Width];
        };
        PlayField.prototype.addOffset = function (x, y, value) {
            this.pieces[x + y * FieldConstants.Width] += value;
        };
        PlayField.prototype.set = function (x, y, piece) {
            this.setAt(x + y * FieldConstants.Width, piece);
        };
        PlayField.prototype.setAt = function (index, piece) {
            this.pieces[index] = piece;
        };
        PlayField.prototype.fill = function (_a) {
            var type = _a.type, rotation = _a.rotation, x = _a.x, y = _a.y;
            var blocks = getBlocks(type, rotation);
            for (var _i = 0, blocks_1 = blocks; _i < blocks_1.length; _i++) {
                var block = blocks_1[_i];
                var _b = [x + block[0], y + block[1]], nx = _b[0], ny = _b[1];
                this.set(nx, ny, type);
            }
        };
        PlayField.prototype.fillAll = function (positions, type) {
            for (var _i = 0, positions_1 = positions; _i < positions_1.length; _i++) {
                var _a = positions_1[_i], x = _a.x, y = _a.y;
                this.set(x, y, type);
            }
        };
        PlayField.prototype.clearLine = function () {
            var newField = this.pieces.concat();
            var top = this.pieces.length / FieldConstants.Width - 1;
            for (var y = top; 0 <= y; y -= 1) {
                var line = this.pieces.slice(y * FieldConstants.Width, (y + 1) * FieldConstants.Width);
                var isFilled = line.every(function (value) { return value !== defines_1.Piece.Empty; });
                if (isFilled) {
                    var bottom = newField.slice(0, y * FieldConstants.Width);
                    var over = newField.slice((y + 1) * FieldConstants.Width);
                    newField = bottom.concat(over, Array.from({ length: FieldConstants.Width }).map(function () { return defines_1.Piece.Empty; }));
                }
            }
            this.pieces = newField;
        };
        PlayField.prototype.up = function (blockUp) {
            this.pieces = blockUp.pieces.concat(this.pieces).slice(0, this.length);
        };
        PlayField.prototype.mirror = function () {
            var newField = [];
            for (var y = 0; y < this.pieces.length; y += 1) {
                var line = this.pieces.slice(y * FieldConstants.Width, (y + 1) * FieldConstants.Width);
                line.reverse();
                for (var _i = 0, line_1 = line; _i < line_1.length; _i++) {
                    var obj = line_1[_i];
                    newField.push(obj);
                }
            }
            this.pieces = newField;
        };
        PlayField.prototype.shiftToLeft = function () {
            var height = this.pieces.length / 10;
            for (var y = 0; y < height; y += 1) {
                for (var x = 0; x < FieldConstants.Width - 1; x += 1) {
                    this.pieces[x + y * FieldConstants.Width] = this.pieces[x + 1 + y * FieldConstants.Width];
                }
                this.pieces[9 + y * FieldConstants.Width] = defines_1.Piece.Empty;
            }
        };
        PlayField.prototype.shiftToRight = function () {
            var height = this.pieces.length / 10;
            for (var y = 0; y < height; y += 1) {
                for (var x = FieldConstants.Width - 1; 1 <= x; x -= 1) {
                    this.pieces[x + y * FieldConstants.Width] = this.pieces[x - 1 + y * FieldConstants.Width];
                }
                this.pieces[y * FieldConstants.Width] = defines_1.Piece.Empty;
            }
        };
        PlayField.prototype.shiftToUp = function () {
            var blanks = Array.from({ length: 10 }).map(function () { return defines_1.Piece.Empty; });
            this.pieces = blanks.concat(this.pieces).slice(0, this.length);
        };
        PlayField.prototype.shiftToBottom = function () {
            var blanks = Array.from({ length: 10 }).map(function () { return defines_1.Piece.Empty; });
            this.pieces = this.pieces.slice(10, this.length).concat(blanks);
        };
        PlayField.prototype.toArray = function () {
            return this.pieces.concat();
        };
        Object.defineProperty(PlayField.prototype, "numOfBlocks", {
            get: function () {
                return this.pieces.length;
            },
            enumerable: true,
            configurable: true
        });
        PlayField.prototype.copy = function () {
            return new PlayField({ pieces: this.pieces.concat(), length: this.length });
        };
        PlayField.prototype.toShallowArray = function () {
            return this.pieces;
        };
        PlayField.prototype.clearAll = function () {
            this.pieces = this.pieces.map(function () { return defines_1.Piece.Empty; });
        };
        PlayField.prototype.equals = function (other) {
            if (this.pieces.length !== other.pieces.length) {
                return false;
            }
            for (var index = 0; index < this.pieces.length; index += 1) {
                if (this.pieces[index] !== other.pieces[index]) {
                    return false;
                }
            }
            return true;
        };
        return PlayField;
    }());
    exports.PlayField = PlayField;
    function getBlockPositions(piece, rotation, x, y) {
        return getBlocks(piece, rotation).map(function (position) {
            position[0] += x;
            position[1] += y;
            return position;
        });
    }
    exports.getBlockPositions = getBlockPositions;
    function getBlockXYs(piece, rotation, x, y) {
        return getBlocks(piece, rotation).map(function (position) {
            return { x: position[0] + x, y: position[1] + y };
        });
    }
    exports.getBlockXYs = getBlockXYs;
    function getBlocks(piece, rotation) {
        var blocks = getPieces(piece);
        switch (rotation) {
            case defines_1.Rotation.Spawn:
                return blocks;
            case defines_1.Rotation.Left:
                return rotateLeft(blocks);
            case defines_1.Rotation.Reverse:
                return rotateReverse(blocks);
            case defines_1.Rotation.Right:
                return rotateRight(blocks);
        }
        throw new Error('Unsupported block');
    }
    exports.getBlocks = getBlocks;
    function getPieces(piece) {
        switch (piece) {
            case defines_1.Piece.I:
                return [[0, 0], [-1, 0], [1, 0], [2, 0]];
            case defines_1.Piece.T:
                return [[0, 0], [-1, 0], [1, 0], [0, 1]];
            case defines_1.Piece.O:
                return [[0, 0], [1, 0], [0, 1], [1, 1]];
            case defines_1.Piece.L:
                return [[0, 0], [-1, 0], [1, 0], [1, 1]];
            case defines_1.Piece.J:
                return [[0, 0], [-1, 0], [1, 0], [-1, 1]];
            case defines_1.Piece.S:
                return [[0, 0], [-1, 0], [0, 1], [1, 1]];
            case defines_1.Piece.Z:
                return [[0, 0], [1, 0], [0, 1], [-1, 1]];
        }
        throw new Error('Unsupported rotation');
    }
    exports.getPieces = getPieces;
    function rotateRight(positions) {
        return positions.map(function (current) { return [current[1], -current[0]]; });
    }
    function rotateLeft(positions) {
        return positions.map(function (current) { return [-current[1], current[0]]; });
    }
    function rotateReverse(positions) {
        return positions.map(function (current) { return [-current[0], -current[1]]; });
    }

    },{"./defines":7}],11:[function(require,module,exports){
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var defines_1 = require("./defines");
    var Operation;
    (function (Operation) {
        Operation["Direct"] = "direct";
        Operation["Swap"] = "swap";
        Operation["Stock"] = "stock";
    })(Operation || (Operation = {}));
    var Quiz = /** @class */ (function () {
        function Quiz(quiz) {
            this.quiz = Quiz.verify(quiz);
        }
        Object.defineProperty(Quiz.prototype, "next", {
            get: function () {
                var index = this.quiz.indexOf(')') + 1;
                var name = this.quiz[index];
                if (name === undefined || name === ';') {
                    return '';
                }
                return name;
            },
            enumerable: true,
            configurable: true
        });
        Quiz.isQuizComment = function (comment) {
            return comment.startsWith('#Q=');
        };
        Quiz.create = function (first, second) {
            var create = function (hold, other) {
                var parse = function (s) { return s ? s : ''; };
                return new Quiz("#Q=[" + parse(hold) + "](" + parse(other[0]) + ")" + parse(other.substring(1)));
            };
            return second !== undefined ? create(first, second) : create(undefined, first);
        };
        Quiz.trim = function (quiz) {
            return quiz.trim().replace(/\s+/g, '');
        };
        Object.defineProperty(Quiz.prototype, "least", {
            get: function () {
                var index = this.quiz.indexOf(')');
                return this.quiz.substr(index + 1);
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Quiz.prototype, "current", {
            get: function () {
                var index = this.quiz.indexOf('(') + 1;
                var name = this.quiz[index];
                if (name === ')') {
                    return '';
                }
                return name;
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Quiz.prototype, "hold", {
            get: function () {
                var index = this.quiz.indexOf('[') + 1;
                var name = this.quiz[index];
                if (name === ']') {
                    return '';
                }
                return name;
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Quiz.prototype, "leastAfterNext2", {
            get: function () {
                var index = this.quiz.indexOf(')');
                if (this.quiz[index + 1] === ';') {
                    return this.quiz.substr(index + 1);
                }
                return this.quiz.substr(index + 2);
            },
            enumerable: true,
            configurable: true
        });
        Quiz.prototype.getOperation = function (used) {
            var usedName = defines_1.parsePieceName(used);
            var current = this.current;
            if (usedName === current) {
                return Operation.Direct;
            }
            var hold = this.hold;
            if (usedName === hold) {
                return Operation.Swap;
            }
            // µ¼íπü«πâƒπâÄπéÆσê⌐τö¿πüºπüìπéï
            if (hold === '') {
                if (usedName === this.next) {
                    return Operation.Stock;
                }
            }
            else {
                if (current === '' && usedName === this.next) {
                    return Operation.Direct;
                }
            }
            throw new Error("Unexpected hold piece in quiz: " + this.quiz);
        };
        Object.defineProperty(Quiz.prototype, "leastInActiveBag", {
            get: function () {
                var separateIndex = this.quiz.indexOf(';');
                var quiz = 0 <= separateIndex ? this.quiz.substring(0, separateIndex) : this.quiz;
                var index = quiz.indexOf(')');
                if (quiz[index + 1] === ';') {
                    return quiz.substr(index + 1);
                }
                return quiz.substr(index + 2);
            },
            enumerable: true,
            configurable: true
        });
        Quiz.verify = function (quiz) {
            var replaced = this.trim(quiz);
            if (replaced.length === 0 || quiz === '#Q=[]()' || !quiz.startsWith('#Q=')) {
                return quiz;
            }
            if (!replaced.match(/^#Q=\[[TIOSZJL]?]\([TIOSZJL]?\)[TIOSZJL]*;?.*$/i)) {
                throw new Error("Current piece doesn't exist, however next pieces exist: " + quiz);
            }
            return replaced;
        };
        Quiz.prototype.direct = function () {
            if (this.current === '') {
                var least = this.leastAfterNext2;
                return new Quiz("#Q=[" + this.hold + "](" + least[0] + ")" + least.substr(1));
            }
            return new Quiz("#Q=[" + this.hold + "](" + this.next + ")" + this.leastAfterNext2);
        };
        Quiz.prototype.swap = function () {
            if (this.hold === '') {
                throw new Error("Cannot find hold piece: " + this.quiz);
            }
            var next = this.next;
            return new Quiz("#Q=[" + this.current + "](" + next + ")" + this.leastAfterNext2);
        };
        Quiz.prototype.stock = function () {
            if (this.hold !== '' || this.next === '') {
                throw new Error("Cannot stock: " + this.quiz);
            }
            var least = this.leastAfterNext2;
            var head = least[0] !== undefined ? least[0] : '';
            if (1 < least.length) {
                return new Quiz("#Q=[" + this.current + "](" + head + ")" + least.substr(1));
            }
            return new Quiz("#Q=[" + this.current + "](" + head + ")");
        };
        Quiz.prototype.operate = function (operation) {
            switch (operation) {
                case Operation.Direct:
                    return this.direct();
                case Operation.Swap:
                    return this.swap();
                case Operation.Stock:
                    return this.stock();
            }
            throw new Error('Unexpected operation');
        };
        Quiz.prototype.format = function () {
            var quiz = this.nextIfEnd();
            if (quiz.quiz === '#Q=[]()') {
                return new Quiz('');
            }
            var current = quiz.current;
            var hold = quiz.hold;
            if (current === '' && hold !== '') {
                return new Quiz("#Q=[](" + hold + ")" + quiz.least);
            }
            if (current === '') {
                var least = quiz.least;
                var head = least[0];
                if (head === undefined) {
                    return new Quiz('');
                }
                if (head === ';') {
                    return new Quiz(least.substr(1));
                }
                return new Quiz("#Q=[](" + head + ")" + least.substr(1));
            }
            return quiz;
        };
        Quiz.prototype.getHoldPiece = function () {
            if (!this.canOperate()) {
                return defines_1.Piece.Empty;
            }
            var name = this.hold;
            if (name === undefined || name === '' || name === ';') {
                return defines_1.Piece.Empty;
            }
            return defines_1.parsePiece(name);
        };
        Quiz.prototype.getNextPieces = function (max) {
            if (!this.canOperate()) {
                return max !== undefined ? Array.from({ length: max }).map(function () { return defines_1.Piece.Empty; }) : [];
            }
            var names = (this.current + this.next + this.leastInActiveBag).substr(0, max);
            if (max !== undefined && names.length < max) {
                names += ' '.repeat(max - names.length);
            }
            return names.split('').map(function (name) {
                if (name === undefined || name === ' ' || name === ';') {
                    return defines_1.Piece.Empty;
                }
                return defines_1.parsePiece(name);
            });
        };
        Quiz.prototype.toString = function () {
            return this.quiz;
        };
        Quiz.prototype.canOperate = function () {
            var quiz = this.quiz;
            if (quiz.startsWith('#Q=[]();')) {
                quiz = this.quiz.substr(8);
            }
            return quiz.startsWith('#Q=') && quiz !== '#Q=[]()';
        };
        Quiz.prototype.nextIfEnd = function () {
            if (this.quiz.startsWith('#Q=[]();')) {
                return new Quiz(this.quiz.substr(8));
            }
            return this;
        };
        return Quiz;
    }());
    exports.Quiz = Quiz;

    },{"./defines":7}]},{},[1]);
