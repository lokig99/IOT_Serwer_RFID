1.	Przygotowanie systemu do pierwszego uruchomienia

	1.1.	Terminal

		1.1.1.	 Zanim uruchomisz program po raz pierwszy powinieneś przygotować plik konfiguracyjny. 
			 W folderze powinien znajdować się plik „config.py.dist”. Należy zmienić jego nazwę na „config.py”. 
		1.1.2.	 Następnie otwórz ten plik za pomocą dowolnego edytora tekstowego.
		1.1.3.	 W pliku można zmienić dwie wartości: __TERMINAL_ID__ oraz __BROKER__. 
			 Pierwszy to identyfikator terminala i za jego pomocą będzie można go zidentyfikować w sieci MQTT. 
			 Powinien być wyjątkowy dla każdego terminala w sieci i składać się tylko z cyfr, liter oraz znaków: ( - ) oraz (  _  ). 
			 Drugie to adres brokera MQTT. Powinien być to adres IP komputera, na którym jest uruchomiony jest broker MQTT.

	1.2.	Aplikacja-serwer

		1.2.1.	 Zanim uruchomisz program po raz pierwszy powinieneś wykonać kroki w ten sam sposób co w przypadku terminala. 
		1.2.2.	 Szczególną uwagę należy zwrócić na wartość __BROADCAST_INTERVAL__, 
			 która pozwala ustawić w jakich odstępach czasu serwer będzie wysyłał wiadomość w sieci MQTT 
			 w celu znalezienia aktualnie dostępnych terminali.

2.	Uruchomienie systemu

	2.1.	Terminal

		2.1.1.	 Po skonfigurowaniu pliku „config.py” w celu uruchomienia terminala należy w konsoli przejść do folderu terminala 
			 i użyć komendy:  $python terminal.py. W obecnej wersji jeżeli uruchamia się program na systemie Linux to trzeba 
			 uruchamiać go jako sudo, ponieważ moduł do obsługi klawiatury (wykrywanie wciśnięcia klawiszy) wymaga uprawnień roota.

	2.2.	Aplikacja-serwer

		2.2.1.	 Po skonfigurowaniu pliku „config.py” w celu uruchomienia terminala należy w konsoli przejść do folderu serwera
			 i użyć komendy:  $python consoleApp.py.

3.	Obsługa systemu

	3.1.	Terminal

		3.1.1.	 Po uruchomieniu program nie wymaga żadnej dalszej obsługi ani konfiguracji. 
		3.1.2.	 W celu zasymulowania zeskanowania karty RFID w terminalu należy wcisnąć kombinację klawiszy: Ctrl + (1-8). 
			 Każda kombinacja odpowiada innej karcie z różnym numerem UID.
		3.1.3.	 W celu wyłączenia terminala należy w oknie programu wpisać „stop” i wcisnąć enter.
		3.1.4.	 Po wyłączeniu programu logi są zapisywane do archiwum zip o nazwie „logs.zip” 
			 (jeżeli takowy nie istnieje to zostanie automatycznie utworzony nowy). Przechowywane są tam wszystkie logi z każdej sesji. 

	3.2.	Aplikacja-serwer

		3.2.1.	 Po uruchomieniu aplikacji pojawi się menu główne (Rysunek 3). 
		3.2.2.	 W menu głównym znajdują się 4 opcje:

			a)	Manage terminals – sekcja zarządzania terminalami. Znajdują się tam opcje dodawania oraz usuwania terminali, 
				które nasłuchuje serwer (w programie terminale przechowywane są w whiteliście – plik whitelist.txt generowany przez program). 
				Dodatkowo można tam wyświetlić dodane terminale oraz terminale dostępne w sieci.
			b)	Manage employees – sekcja zarządzania bazą danych pracowników. Są tam opcje do wyświetlenia wszystkich pracowników, 
				dodawania i usuwania nowych pracowników (Uwaga! Jeżeli zostanie w terminalu użyta karta RFID bez przypisanego do niej pracownika 
				to zostanie utworzony anonimowy pracownik z przypisanym do niego numerem UID karty). Dodatkowe opcje to modyfikacja danych pracowników
				jak imię i karta RFID, oraz opcja służąca do generowani raportów.
			c)	Show server logs – wyświetla logi serwera.
			d)	Stop server and quit – zatrzymuje serwer I wyłącza aplikację

		3.2.3.	 Po wyłączeniu programu logi są zapisywane do archiwum zip o nazwie „logs.zip” (jeżeli takowy nie istnieje to zostanie automatycznie utworzony nowy). 
		         Przechowywane są tam wszystkie logi z każdej sesji. 

