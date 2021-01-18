from django.shortcuts import render, redirect, get_object_or_404

# importamos el form para crear un usuario, y para logearlo
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# importmos el error para usar, cuando son iguales los usuarios
from django.db import IntegrityError
# una vez que se registra debemos logearlo, y para desloguearlo
from django.contrib.auth import login, logout, authenticate
from todo.forms import TodoForm
from todo.models import Todo
from django.utils import timezone

# esto es solo para que ciertos usuarios puedan acceder a ciertas paginas
from django.contrib.auth.decorators import login_required
# PARA QUE EL USUARIO NO LOGEADO que entra en /CREATE por ejemplo, y no
# le de un 404 feo, vamos a settings.py y agregamos esto
# LOGIN_URL = '/login'


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):

    if request.method == 'GET':  # si alguien ingresa en la pagina nomas
        return render(request, 'todo/signupuser.html',
                      {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:

            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password2'])

                print(request.POST['password1'])
                print(request.POST['password2'])
                user.save()

                # una vez que se registra lo mandamos logeamos
                login(request, user)
                # ahora lo mandamos a alguna pagina,para hacer
                # esto necesitamos
                # otra cosa que no sea el render, para que lo redirija
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(),
                               'error': 'That username has already been taken. Please choose a new username'})

                # Una ves que hace esto y guarda el objeto,
                # debo mandarlo a otra pagina,
                # sino da error

        else:
            # si le erra los dos password pasa esto
            # le devuelvo a la misma pagina del form, y
            # le muestro un mensaje
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Password did not match'})


@login_required
def createtodo(request):
    # si el usuario entra nomas al form sin  hacer Post/submit
    if request.method == 'GET':
        # tenemos que crear nuestro form.py para esto, ya que por ejemplo
        # el del usuario lo crea django solo
        return render(request, 'todo/createtodo.html',
                      {'form': TodoForm()})
    else:

        try:
            form = TodoForm(request.POST)
            # creamos el Todo, pero no lo metemos en la base de datos
            # porque falta el usuario
            newtodo = form.save(commit=False)
            # asi le asignamos el usuario y despues lo metemos al todo
            newtodo.user = request.user
            # ahora lo guardamos
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html',
                          {'form': TodoForm(), 'error': 'Bad data passed in'})


@login_required
def currenttodos(request):
    # todos = Todo.objects.all() #eso me da todo, pero yo quiero lo
    # que pertenezcan al usuario logeado
    # tambien quiero los que NO ESTEN COMPLETOS,
    # osea que no tengan fecha de completado
    # en django se hace "atributo__isnull"
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos': todos})


@login_required
def completedtodos(request):
 # el order by  "-" es de la fecha mas reciente a la vieja
    todos = Todo.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos': todos})


@login_required
def viewtodo(request, todo_pk):
    #  user=request.user importante porque sino cualquier usuario
    # ingresa en el navegador/todo/200 y modifica el id 200 por mas
    # que no le pertenezca a el,
    # si ingresa a el 200 y no es de el devuelve 404
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'GET':
        # esto es para que se muestre todo como un form y ya se pueda editar y todo
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            # acordarse de la instancia
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')

        except ValueError:
            return render(request, 'todo/viewtodo.html',
                          {'todo': todo, 'form': form, 'error': 'Bad Info'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html',
                      {'form': AuthenticationForm()})
    else:
        # para comprobar que el usuario y la contraseña son correctos
        # importamos  authenticate

        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])
        # si no coincide user es vacio/none

        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'form': AuthenticationForm(),
                           'error': 'Username and password did not match'})
        else:  # si existe
            login(request, user)
            return redirect('currenttodos')
