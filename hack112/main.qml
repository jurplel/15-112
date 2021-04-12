import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.15
import QtWebEngine 1.3
import QtQuick.Layouts 1.15
import QtMultimedia 5.15

Window {
    width: 1280
    height: 705
    maximumHeight: height
    maximumWidth: width

    minimumHeight: height
    minimumWidth: width

    visible: true
    title: qsTr("All-Nighter Simulator 2021")
    color: "black"

    property int solved: 0
    onSolvedChanged: {
        if (solved >= 7) {
            globalTimer.stop()
            updateTimer.stop()
            chocoTimer.stop()
            rbcanTimer.stop()
            winScreen.visible = true
        }
    }

    Timer {
        id: globalTimer
        interval: 1500
        repeat: true
        running: false
        onTriggered: {
            hanger.decreaseHanger(1)
            physicalHealth.decreaseHealth(1)
            sanity.decreaseSanity(1)
        }
    }
    Timer {
        id: updateTimer
        interval: 50
        repeat: true
        running: false
        onTriggered: {
            hangerBar.value = hanger.getHanger()
            healthBar.value = physicalHealth.getHealth()
            sanityBar.value = sanity.getSanity()
            clock.text = timeElapsed.returnGameTimeString()
            let hrs = timeElapsed.returnInGameTime()[0]
            if (hrs >= 7 && hrs < 9) {
                globalTimer.stop()
                updateTimer.stop()
                chocoTimer.stop()
                rbcanTimer.stop()
                loseScreen.visible = true
            }
            kosbie.visible = sanity.getSanity() < 20
            axolotl.visible = sanity.getSanity() < 50
        }
    }

    Image {
        source: "mainbg.jpg"
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
    }

    Label {
        id: clock
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: 10
        anchors.topMargin: 10
        width: parent.width/10
        height: parent.height/10
        color: "white"
        font.pixelSize: 16
        style: Text.Outline
        styleColor: "black"
    }

    GridLayout {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: 10
        anchors.topMargin: 60
        width: parent.width/10
        height: parent.height/10
        columns: 2
        Label {
            text: "Sanity"
            color: "white"
        }
        ProgressBar {
            id: sanityBar
            value: sanity.getSanity()
            to: 100
            Layout.fillWidth: true
            width: 100
        }
        Label {
            text: "Hangry"
            color: "white"
        }
        ProgressBar {
            id: hangerBar
            value: hanger.getHanger()
            to: 100
            Layout.fillWidth: true
            width: 100
        }
        Label {
            text: "Tiredness"
            color: "white"
        }
        ProgressBar {
            id: healthBar
            value: physicalHealth.getHealth()
            to: 100
            Layout.fillWidth: true
        }
    }

    Item {
        id: display
        anchors.fill: parent
        anchors.leftMargin: parent.width*0.29
        anchors.rightMargin: parent.width*0.31
        anchors.bottomMargin: parent.height*0.4
        anchors.topMargin: parent.height*0.15

        Image {
            source: "ielogo.png"
            width: parent.width*0.12
            fillMode: Image.PreserveAspectFit
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.topMargin: parent.height*0.05
            anchors.leftMargin: parent.width*0.05

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: { webbrowse.visible = true }
            }
        }

        Image {
            source: "vscodelogo.png"
            width: parent.width*0.11
            fillMode: Image.PreserveAspectFit
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.topMargin: parent.height*0.28
            anchors.leftMargin: parent.width*0.06

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: { vscode.visible = true }
            }
        }

        Image {
            id: kosbie
            source: "dkosbie.png"
            visible: false
            width: parent.width*0.11
            fillMode: Image.PreserveAspectFit
            anchors.fill: parent
            opacity: 0.1
        }

        Item {
            id: webbrowse
            visible: false
            onVisibleChanged: {
                if (visible == true) {
                    webbrowser.url = "https://www.youtube.com/watch?v=8LFoPY6NFRg"
                } else {
                    webbrowser.url = "about:blank"
                }
            }
            anchors.fill: parent
            TextField {
                id: webbrowseurl
                placeholderText: "URL"
                anchors.fill: parent
                anchors.bottomMargin: parent.height/10*9
                anchors.rightMargin: parent.width/20
                text: "https://www.youtube.com/watch?v=8LFoPY6NFRg"
                onEditingFinished: webbrowser.url = text
                selectByMouse: true
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.IBeamCursor
                    acceptedButtons: Qt.NoButton
                }
            }

            Button {
                anchors.fill: parent
                anchors.bottomMargin: parent.height/10*9
                anchors.leftMargin: parent.width/20*19
                text: "X"
                onClicked: webbrowse.visible = false
            }

            WebEngineView {
                id: webbrowser
                anchors.fill: parent
                anchors.topMargin: parent.height/10
                zoomFactor: 0.75
                onUrlChanged: webbrowseurl.text = url
            }

            Timer {
                id: webbrowseTimer
                interval: 200
                repeat: true
                running: webbrowse.visible
                onTriggered: {
                    sanity.increaseSanity(1)
                }
            }
        }

        Rectangle {
            id: vscode
            visible: false
            anchors.fill: parent
            color: "#1E1E1E"

            Rectangle {
                anchors.fill: parent
                anchors.topMargin: parent.height/20*19
                color: "#007ACC"
            }

            Rectangle {
                anchors.fill: parent
                anchors.bottomMargin: parent.height/10*9
                color: "#333333"
            }

            Rectangle {
                anchors.fill: parent
                anchors.rightMargin: parent.width/15*14
                anchors.bottomMargin: parent.height/20
                color: "#333333"
            }

            Button {
                anchors.fill: parent
                anchors.bottomMargin: parent.height/10*9
                anchors.leftMargin: parent.width/20*19
                text: "X"
                onClicked: vscode.visible = false
            }


            ColumnLayout {
                id: qnalayout
                anchors.left: parent.left
                anchors.leftMargin: parent.width/15+10
                anchors.top: parent.top
                anchors.topMargin: parent.height/10+10
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.bottomMargin: parent.height/10

                function newQuestion() {
                    let qna = qanda.makeQandA()
                    question.text = qna[0]
                    answer.answr = qna[1]
                    answer.text = ""
                }

                Label {
                    Component.onCompleted: qnalayout.newQuestion()
                    id: question
                    text: "What's a question sdnfrsdnfdjsdfkjdsnknfjfsdknfjdks ERROR"
                    color: "white"
                    font.pixelSize: 26
                    font.weight: Font.Medium
                    style: Text.Outline
                    styleColor: "black"
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }
                
                RowLayout {
                    spacing: 0

                    TextField {
                        id: answer
                        property string answr: ""
                        function checkAnswer() {
                            if (answer.text == answer.answr) {
                                correctorincorrectbit.text = "✔️"
                                solved += 1
                                sanity.increaseSanity(1) // every little bit counts
                            } else {
                                correctorincorrectbit.text = "✖️"
                                sanity.decreaseSanity(5)
                                punch.play()
                            }
                            correctorincorrectbit.text += "\n" + answer.answr
                            qnalayout.newQuestion()
                        }
                        onAccepted: checkAnswer()
                        Audio {
                            id: punch
                            source: "PUNCH.wav"
                        }
                    }

                    Button {
                        text: "✔️"
                        Layout.preferredWidth: 30
                        onClicked: answer.checkAnswer()
                    }
                }

                Label {
                    id: correctorincorrectbit
                    color: "white"
                    font.pixelSize: 24
                    font.weight: Font.Medium
                    style: Text.Outline
                    styleColor: "black"
                    wrapMode: Text.WrapAnywhere
                    onTextChanged: correctorincorrectbitresettimerbit.start()
                    Timer {
                        id: correctorincorrectbitresettimerbit
                        interval: 1200
                        onTriggered: parent.text = ""
                    }
                }
                
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }

    Timer {
        id: chocoTimer
        interval: 40000
        onTriggered: {
            choco.visible = true
        }
    }

    Image {
        id: choco
        source: "chocolate.png"
        visible: false
        width: parent.width*0.11
        fillMode: Image.PreserveAspectFit
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.bottomMargin: parent.height*0.02
        anchors.leftMargin: parent.width*0.02
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                chocoTimer.start()
                hanger.increaseHanger(100)
                choco.visible = false
            }
        }
    }

    Timer {
        id: rbcanTimer
        interval: 30000
        onTriggered: {
            rbcan.visible = true
        }
    }

    Image {
        id: rbcan
        source: "rbcan.png"
        visible: false
        width: parent.width*0.08
        fillMode: Image.PreserveAspectFit
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.bottomMargin: parent.height*0.13
        anchors.leftMargin: parent.width*0.17
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                rbcanTimer.start()
                physicalHealth.increaseHealth(100)
                rbcan.visible = false
            }
        }
    }

    Image {
        id: axolotl
        source: "axolotl.png"
        visible: false
        opacity: 0.4
        width: parent.width*0.11
        fillMode: Image.PreserveAspectFit
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: parent.height/25
        anchors.rightMargin: parent.width/9
    }

    Item {
        id: menu
        anchors.fill: parent

        Image {
            source: "menubg.jpeg"
            fillMode: Image.PreserveAspectFit
            anchors.fill: parent
        }

        Label {
            text: qsTr("All-Nighter Simulator 2021")
            color: "white"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 64
            font.pixelSize: 48
            font.italic: true
            font.weight: Font.Medium
            style: Text.Outline
            styleColor: "black"
        }

        Button {
            text: qsTr("Play :D")
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 128
            onClicked: {
                menu.visible = false
                globalTimer.start()
                updateTimer.start()
                chocoTimer.start()
                rbcanTimer.start()
            }
        }
    }

    Rectangle {
        id: winScreen
        color: "black"

        visible: false
        onVisibleChanged: {
            if (visible == true) {
                megaloMusic.play()
            } else {
                megaloMusic.stop()
            }
        }

        anchors.fill: parent

        Label {
            text: qsTr("You \"Win\"")
            color: "white"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            font.pixelSize: 48
            font.italic: true
            font.weight: Font.Medium
            style: Text.Outline
            styleColor: "black"
        }
        Audio {
            id: megaloMusic
            source: "megalovania.mp3"
            volume: 0.2
        }
    }

    Rectangle {
        id: loseScreen
        color: "black"

        visible: false
        onVisibleChanged: {
            if (visible == true) {
                loseMusic.play()
            } else {
                loseMusic.stop()
            }
        }

        anchors.fill: parent

        Label {
            text: qsTr("You Lose!")
            color: "white"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            font.pixelSize: 48
            font.italic: true
            font.weight: Font.Medium
            style: Text.Outline
            styleColor: "black"
        }
        Audio {
            id: loseMusic
            source: "coffindance.mp3"
            volume: 0.2
        }
    }
}