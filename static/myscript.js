window.onload = function() {

    new AirDatepicker('#airdatepicker', {
		isMobile: true,
    	autoClose: true,
    	buttons: ['today', 'clear'],
    	minDate: new Date(),
		timepicker: true,
	});


    // --------------------- AJAX запрос на запуск сервера ---------------------------
    // info - данные в формате JSON, передаваемые на сервер
    // link - ссылка на сервер
	function runServer(info, link){

		$.ajax({
			method: 'POST',
			url: link,
			dataType: 'json',
			data: info,
			contentType: "application/json",
			contentType: 'application/json;charset=UTF-8',
			success: function(data){
				console.log(data);

			}
		});
	}

	$(".server_pyopenssl_runServer").on('click', function(){
	    // ---------------------------- Формируем JSON для отправки в функцию обработки Flask ---------------------------------
	    var id = $(this).attr("data-id")
	    var action = $(this).attr("data-action")
        var info = JSON.stringify({id: id, action: action});
        console.log(action);
        runServer(info, "/server_pyopenssl/runServer");
	})

	// --------------------- AJAX запрос на запуск сервера ---------------------------


	// --------------------- Правила валидации форм ---------------------------
        // Поле name должно быть от 5 до 20 символов
        var rule_name = {
            range: {
                min: 5,
                max: 20
            }
        };

        // Поле description должно быть от 5 символов
        var rule_descr = {
            min: 5
        };

    // Подсвечиваем рамку поля ввода и отображаем предупреждение
        // obj1 - JQuery объект рамки, которую будем подсвечивать
        // obj2 - JQuery объект блока, который будем показывать
        // show - 1 - показать предупреждение, 0 - скрыть
        function alert_check(obj1, obj2, show){
            if (show == 1){
                obj1.addClass('is-invalid');
			    obj2.removeClass('d-none');
            }else{
                obj1.removeClass('is-invalid');
	            obj2.addClass('d-none');
            }

        }

    // --------------------- Правила валидации форм ---------------------------

    // --------------------- AJAX запрос на создание нового узла---------------------------
    // info - данные в формате JSON, передаваемые на сервер
    // link - ссылка на сервер
	function makeRequest(info, link){

		$.ajax({
			method: 'POST',
			url: link,
			dataType: 'json',
			data: info,
			contentType: "application/json",
			contentType: 'application/json;charset=UTF-8',
			success: function(data){
				if (data.coincidence) {
				    // Подсвечиваем рамку поля ввода и отображаем предупреждение если такое имя уже есть
				    alert_check($('input[name=name]'), $('.alert-name'), 1);
				}else if (data.success == 1) {
				    $('.success-create').removeClass('d-none');
				    $('.success-create').addClass('alert-success');
				    $('.success-create').text('Успешно!');
				}else if (data.success == 0) {
                    $('.success-create').removeClass('d-none');
				    $('.success-create').addClass('alert-danger');
				    $('.success-create').text('Ошибка, объект не создан!');
				};

			}
		});
	}

	// --------------------- AJAX запрос на создание нового узла ---------------------------



    // --------------------------- Создание нового ЦС -----------------------------------------------
    $("#create_ca").on('click', function(){

        // ---------------------------- Формируем JSON для отправки в функцию обработки Flask ---------------------------------
        var info = JSON.stringify({name: $('input[name=name]').val(), descr: $('input[name=descr]').val(), validity: $('input[name=validity]').val()});


        // ----------------------------- Проводим валидацию форм -----------------------------------------
		var valid_input_name = approve.value($('input[name=name]').val(), rule_name);
		var valid_input_descr = approve.value($('input[name=descr]').val(), rule_descr);

		if (valid_input_name.approved == false){
		    alert_check($('input[name=name]'), $('.alert-name'), 1);
		}

		if (valid_input_descr.approved == false){
		    alert_check($('input[name=descr]'), $('.alert-descr'), 1);
		}

		// ------------------- Если первоначальная валидация прошла успешно, выполняем POST запрос на сервер -----------------------------
		if (valid_input_name.approved && valid_input_descr.approved){
		    makeRequest(info, '/ca_pyopenssl/create');
		}

		console.log(valid_input_name.approved);
	})

	// --------------------------- Создание нового ЦС -----------------------------------------------






	// --------------------------- Создание нового Сервера -----------------------------------------------
	$("#create_server").on('click', function(){

        // ---------------------------- Формируем JSON для отправки в функцию обработки Flask ---------------------------------
        var info = JSON.stringify({name: $('input[name=name]').val(), descr: $('input[name=descr]').val(), validity: $('input[name=validity]').val(), select_ca: $('select[name=select_ca]').val()});

        // ----------------------------- Проводим валидацию форм -----------------------------------------
		var valid_input_name = approve.value($('input[name=name]').val(), rule_name);
		var valid_input_descr = approve.value($('input[name=descr]').val(), rule_descr);
		var valid_input_select = approve.value($('select[name=select_ca]').val(), rule_name);

		if (valid_input_name.approved == false){
            alert_check($('input[name=name]'), $('.alert-name'), 1);
		}

        if (valid_input_descr.approved == false){
		    alert_check($('input[name=descr]'), $('.alert-descr'), 1);
		}

		if (valid_input_select.approved == false){
            alert_check($('select[name=select_ca]'), $('.alert-select'), 1);
		}

		// ------------------- Если первоначальная валидация прошла успешно, выполняем POST запрос на сервер -----------------------------
		if (valid_input_name.approved && valid_input_descr.approved && valid_input_select.approved){
		    makeRequest(info, "/server_pyopenssl/create");
		}

		console.log(valid_input_name.approved);


        console.log(valid_input_name);
	});
	// --------------------------- Создание нового Сервера -----------------------------------------------





	// --------------------------- Создание нового Клиента -----------------------------------------------
	$("#create_client").on('click', function(){

        // ---------------------------- Формируем JSON для отправки в функцию обработки Flask ---------------------------------
        var info = JSON.stringify({name: $('input[name=name]').val(), descr: $('input[name=descr]').val(), validity: $('input[name=validity]').val(), select_server: $('select[name=select_server]').val()});
        //console.log(info)
        // ----------------------------- Проводим валидацию форм -----------------------------------------
		var valid_input_name = approve.value($('input[name=name]').val(), rule_name);
		var valid_input_descr = approve.value($('input[name=descr]').val(), rule_descr);
		var valid_input_select = approve.value($('select[name=select_server]').val(), rule_name);

		if (valid_input_name.approved == false){
            alert_check($('input[name=name]'), $('.alert-name'), 1);
		}

        if (valid_input_descr.approved == false){
		    alert_check($('input[name=descr]'), $('.alert-descr'), 1);
		}

		if (valid_input_select.approved == false){
            alert_check($('select[name=select_server]'), $('.alert-select'), 1);
		}

		// ------------------- Если первоначальная валидация прошла успешно, выполняем POST запрос на сервер -----------------------------
		if (valid_input_name.approved && valid_input_descr.approved && valid_input_select.approved){
		    makeRequest(info, "/client_pyopenssl/create");
		}

	});
	// --------------------------- Создание нового Клиента -----------------------------------------------




    // При фокусе на поле ввода убираем предупреждения
	$("input[name=name]").on('focus', function(){
	    alert_check($('input[name=name]'), $('.alert-name'), 0);
	});

	$("input[name=descr]").on('focus', function(){
	    alert_check($('input[name=descr]'), $('.alert-descr'), 0);
	});

	$("select[name=select_ca]").on('focus', function(){
	    alert_check($('select[name=select_ca]'), $('.alert-select'), 0);
	});


	// --------------------------- Список пользователей -----------------------------------------------

        // --------------------------- Удаление пользователя -----------------------------------------------
        // info - данные в формате JSON, передаваемые на сервер
        // link - ссылка на сервер
        // elem - элемент строки DOM, которую будем удалять
        function delUser(info, link, elem){

            $.ajax({
                method: 'POST',
                url: link,
                dataType: 'json',
                data: info,
                contentType: "application/json",
                contentType: 'application/json;charset=UTF-8',
                success: function(data){
                    if (data.success == 1) {
                        console.log(info);
                        elem.animate({
                            'background-color':'red'
                        }, 100).animate({
                            'background-color':'#fff',
                            'display':'none'
                        }, 900);

                        setTimeout(function() {
                            elem.fadeOut('fast');
                        }, 600);
                    }else{
                        console.log(data);
                    }
                }
            });
        }


        $('button').on('click', function(){
            const parent_el = $(this).parent().parent();
            info = JSON.stringify({name: $(this).attr("data-button")});
            console.log(info);
            delUser(info, "/users/del_users", parent_el);
        })
        // --------------------------- Удаление пользователя -----------------------------------------------

        // --------------------------- Активация пользователя -----------------------------------------------
        function activateRequest(info, link){

            $.ajax({
                method: 'POST',
                url: link,
                dataType: 'json',
                data: info,
                contentType: "application/json",
                contentType: 'application/json;charset=UTF-8',
                success: function(data){
                    console.log(data);

                }
            });
        }

        $('.form-check-input').on('click', function(){
            const user = $(this).attr('id');
            info = JSON.stringify({name: user});
            console.log(info);
            activateRequest(info, "/users/activate");
        })
        // --------------------------- Активация пользователя -----------------------------------------------

	// --------------------------- Список пользователей -----------------------------------------------


}