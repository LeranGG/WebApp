window.addEventListener("DOMContentLoaded", () => {
	const tg = window.Telegram?.WebApp;
	if (!tg) return;

	const userId = document.getElementById("user-info");
	const userId2 = document.getElementById("user-info2");
	const renameMenu = document.getElementById("button_rename_menu");
	const rename = document.getElementById("button_rename_user");
	const room = document.getElementById("room");
	const computers = document.getElementById("computers");

	const btn_profile = document.getElementById("btn-profile");
	const btn_shop = document.getElementById("btn-shop");
	const btn_top = document.getElementById("btn-top");

	let selectedComputer = null;

	fetch("/get-user-info", {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: `initData=${encodeURIComponent(tg.initData)}`,
	})
		.then((res) => res.json())
		.then((data) => {
			userId.innerText = `Профиль игрока: ${data.name}`;
			userId2.innerHTML = `Баланс: ${data.balance}<br>Уровень комнаты: ${data.room}<br>Компьютеры: ${data.pcs}/${data.room * 5}`;
		})
		.catch((err) => console.error("Ошибка запроса:" + err));

	renameMenu.addEventListener("click", () => {
		showMenu("rename-menu", "profile-menu");
	});

	rename.addEventListener("click", () => {
		const newName = document.getElementById("username").value;
		fetch("/api/rename", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: `initData=${encodeURIComponent(tg.initData)}&newName=${encodeURIComponent(newName)}`,
		});
		tg.showAlert('Успешно!');
	});

	const allMenus = ["top-menu", "profile-menu", "shop-menu", "room-menu", "computers-menu", "rename-menu"];

	function showMenu(menuIdToShow, hideId = null) {
		allMenus.forEach((id) => {
			const el = document.getElementById(id);
			if (el) el.style.display = id === menuIdToShow ? "block" : "none";
		});
		if (hideId) document.getElementById(hideId).style.display = "none";
	}

	btn_top.addEventListener("click", () => {
		showMenu("top-menu");
		fetch("/api/top", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
		})
			.then((res) => res.json())
			.then((data) => {
				const topUsers = document.getElementById("top-users");
				topUsers.innerHTML = data.users
					.map((player, index) => `${index + 1}. ${player.name} — ${player.bal}<br>`)
					.join("");
			})
			.catch((err) => console.error("Ошибка при получении топа:", err));
	});

	btn_profile.addEventListener("click", () => {
		showMenu("profile-menu");
		fetch("/get-user-info", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: `initData=${encodeURIComponent(tg.initData)}`,
		})
			.then((res) => res.json())
			.then((data) => {
				userId.innerText = `Профиль игрока: ${data.name}`;
				userId2.innerHTML = `Баланс: ${data.balance}<br>Уровень комнаты: ${data.room}<br>Компьютеры: ${data.pcs}/${data.room * 5}`;
			})
			.catch((err) => console.error("Ошибка запроса:" + err));
	});

	btn_shop.addEventListener("click", () => showMenu("shop-menu"));

	room.addEventListener("click", () => {
		showMenu("room-menu");
		fetch("/api/shop_room", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: `initData=${encodeURIComponent(tg.initData)}`,
		})
			.then((res) => res.json())
			.then((data) => {
				const info = document.getElementById("room-lvl");
				info.innerHTML = "Уровень - " + data.lvl;
			})
			.catch((err) => console.error("Ошибка при получении уровня комнаты:", err));
	});

	const dropdownBtn = document.getElementById("dropdownComputer");
	const dropdownList = document.getElementById("computerList");

	computers.addEventListener("click", () => {
		showMenu("computers-menu");
		fetch("/api/shop_pc", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: `initData=${encodeURIComponent(tg.initData)}`,
		})
			.then((res) => res.json())
			.then((data) => {
				data.forEach((pc) => {
					const li = document.createElement("li");
					li.classList.add("dropdown-item");
					li.dataset.id = pc.level;

					li.innerHTML = `
						<span class="item-title">${pc.name}</span><br>
						<span class="item-description">${pc.description}</span>
					`;

					dropdownList.appendChild(li);
				});
			})
			.catch((err) => console.error("Ошибка при получении компьютеров:", err));
	});

	dropdownBtn.addEventListener("click", () => {
		dropdownList.style.display = dropdownList.style.display === "block" ? "none" : "block";
	});

	dropdownList.addEventListener("click", (event) => {
		const item = event.target.closest(".dropdown-item");
		if (!item) return;

		const name = item.querySelector(".item-title").textContent;
		selectedComputer = item.dataset.id;
		dropdownBtn.textContent = name;
		dropdownList.style.display = "none";
	});

	document.addEventListener("click", (e) => {
		if (!document.getElementById("computerDropdown").contains(e.target)) {
			dropdownList.style.display = "none";
		}
	});

	document.getElementById("btn-room").addEventListener("click", () => {
		fetch("/api/buy_room", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: `initData=${encodeURIComponent(tg.initData)}`,
		})
			.then((res) => res.json())
			.then((data) => {
				tg.showAlert(data);
			})
			.catch((err) => console.error("Ошибка при покупке комнаты:", err));
	});

	document.getElementById("upgrades").addEventListener("click", () => {
		tg.showAlert('Пока не доступно');
	});

	document.getElementById("ads").addEventListener("click", () => {
		tg.showAlert('Пока не доступно');
	});

	document.getElementById("buyButton").addEventListener("click", (event) => {
		event.preventDefault();
		const quantityInput = document.getElementById("quantityInput");
		const quantity = parseInt(quantityInput.value);

		if (!selectedComputer) {
			tg.showAlert("Выберите компьютер!");
			return;
		}

		if (isNaN(quantity) || quantity <= 0) {
			tg.showAlert("Введите корректное количество!");
			quantityInput.focus();
			return;
		}

		fetch("/api/buy_pc", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: `initData=${encodeURIComponent(tg.initData)}&quantity=${encodeURIComponent(quantity)}&lvl=${encodeURIComponent(selectedComputer)}`,
		})
			.then((res) => res.json())
			.then((data) => {
				tg.showAlert(data);
			})
			.catch((err) => console.error("Ошибка при покупке компьютеров:", err));
	});
});
