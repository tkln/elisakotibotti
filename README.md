elisakotibotti
==============
Pikaisesti kasaan lätkitty wlanin yli ajeltava tankki. Klienttisofta vaatii python 2.7:n ja pygame.

Käynnistysproseduuri:
-laita virrat päälle pohjan kytkimestä.
  -ota huomioon, että toinen telaketjuista alkaa pyörimään heti käynnistettyä mutta sammuu hetken kuluttua
-odota,purkilla menee minuutti tai pari buutata
-kun indikaattorivalot alkavat vetämään Larson scanneria niin botin softan pitäisi olla tajuissaan
  -botti toimii wlan AP:na ja luo verkon ElisaKotibotti (ei salausta)
-yhdistä verkkoon
-aja client.py

Botin ohjaamiseen voi käyttää hiirtä, näppäimistöä tai joystickiä.
Hiiri toimii painamalla vasenta näppäintä ohjelman ikkunan sisällä.
Näppäimistöllä nuolinäppäimet. Defaulteilla käytetään joystick 0:n akseleita 3 ja 4.
Client.py:n alussa on kapseilla vakioita, joita säätämällä voidaan esimerkiksi konffata joystickin id ja akselit.
