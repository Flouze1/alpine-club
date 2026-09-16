from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

from apps.mountains.models import mountains
from apps.climbers.models import climbers, groups, climber_members
from apps.ascents.models import climbs

try:
    from apps.ascents.models import reports
except ImportError:
    reports = None

@login_required(login_url='/login/')
def home(request):
    current_climber = climbers.objects.filter(email__startswith=request.user.username).first()
    if not current_climber:
        current_climber = climbers.objects.create(
            first_name=request.user.first_name or request.user.username,
            last_name=request.user.last_name or "Участник",
            email=f"{request.user.username}@alpine.local",
            sports_category='новичок',
            schoole=False,
            test=False,
            created_at=timezone.now()
        )

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # 1. Создание группы
        if action == 'create_group':
            if not request.user.is_staff and not (current_climber.schoole and current_climber.test):
                messages.error(request, "Ошибка: У вас нет прав на создание группы.")
            else:
                name = request.POST.get('name')
                mountain_id = request.POST.get('mountain_id')
                max_members = request.POST.get('max_members')
                date_str = request.POST.get('date_start')
                time_str = request.POST.get('time_start')
                
                try:
                    mountain = mountains.objects.get(id=mountain_id)
                    
                    if date_str and time_str:
                        date_val = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    elif date_str:
                        date_val = datetime.strptime(date_str, "%Y-%m-%d")
                    else:
                        date_val = timezone.now()

                    new_group = None
                    for date_field in ['date_formation', 'start_event', 'date_start', 'date', 'created_at', 'start_time']:
                        try:
                            kwargs = {
                                'name': name,
                                'mountain_id': mountain,
                                'max_members': max_members,
                                date_field: date_val
                            }
                            new_group = groups.objects.create(**kwargs)
                            break
                        except Exception:
                            continue
                            
                    if not new_group:
                        new_group = groups.objects.create(name=name, mountain_id=mountain, max_members=max_members)

                    climber_members.objects.create(
                        climber_id=current_climber, 
                        groups_id=new_group, 
                        role=True,
                        joined_date=timezone.now()
                    )
                    messages.success(request, f"Группа '{name}' успешно создана!")
                except Exception as e:
                    messages.error(request, f"Ошибка создания группы: {e}")
                
        # 2. Редактирование группы
        elif action == 'edit_group':
            group_id = request.POST.get('group_id')
            group = get_object_or_404(groups, id=group_id)
            is_leader = climber_members.objects.filter(climber_id=current_climber, groups_id=group, role=True).exists()
            
            if not request.user.is_staff and not is_leader:
                messages.error(request, "Ошибка: Редактировать группу может только её руководитель!")
            else:
                group.name = request.POST.get('name')
                group.max_members = request.POST.get('max_members')
                new_date = request.POST.get('date_start')
                new_time = request.POST.get('time_start')
                
                if new_date:
                    try:
                        if new_time:
                            final_dt = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
                        else:
                            final_dt = datetime.strptime(new_date, "%Y-%m-%d")
                            
                        for date_field in ['date_formation', 'start_event', 'date_start', 'date', 'created_at', 'start_time']:
                            if hasattr(group, date_field):
                                setattr(group, date_field, final_dt)
                                break
                    except Exception:
                        pass
                        
                group.save()
                messages.success(request, f"Группа '{group.name}' успешно обновлена!")

        # 3. Отчёт о восхождении
        elif action == 'create_ascent':
            group_id = request.POST.get('group_id')
            group = get_object_or_404(groups, id=group_id)
            is_leader = climber_members.objects.filter(climber_id=current_climber, groups_id=group, role=True).exists()

            if not request.user.is_staff and not is_leader:
                messages.error(request, "Ошибка: Отчёт может заполнять только руководитель!")
            else:
                date_str = request.POST.get('date_start')
                time_str = request.POST.get('time_start')
                comment_val = request.POST.get('comment')
                grade_val = request.POST.get('grade')
                result_val = request.POST.get('result') == 'on'
                
                try:
                    if date_str and time_str:
                        dt_val = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    elif date_str:
                        dt_val = datetime.strptime(date_str, "%Y-%m-%d")
                    else:
                        dt_val = timezone.now()

                    climb_kwargs = {}
                    for f in [field.name for field in climbs._meta.get_fields()]:
                        if f in ['group', 'group_id', 'groups', 'groups_id']:
                            climb_kwargs[f] = group
                        elif f in ['date_time_start', 'date_start', 'start_event', 'date', 'datetime', 'start_time']:
                            climb_kwargs[f] = dt_val
                        elif f in ['end_event', 'date_time_end', 'end_date', 'end_time']:
                            climb_kwargs[f] = dt_val + timedelta(hours=4)
                        elif f in ['status', 'result', 'результат']:
                            climb_kwargs[f] = "Успех" if result_val else "Отказ"
                        elif f in ['grade', 'оценка', 'score', 'ball']:
                            climb_kwargs[f] = grade_val if grade_val else "5"

                    new_climb = climbs.objects.create(**climb_kwargs)

                    if reports:
                        try:
                            report_kwargs = {
                                'climb_id': new_climb if hasattr(reports, 'climb_id') else None,
                                'summary': comment_val or "",
                                'success': result_val
                            }
                            reports.objects.create(**report_kwargs)
                        except Exception:
                            pass

                    messages.success(request, "Отчёт о восхождении успешно сохранён!")
                except Exception as e:
                    messages.error(request, f"Точная ошибка БД: {str(e)}")

        # 4. Удаление группы
        elif action == 'delete_group':
            group_id = request.POST.get('group_id')
            group = get_object_or_404(groups, id=group_id)
            is_leader = climber_members.objects.filter(climber_id=current_climber, groups_id=group, role=True).exists()
            
            if not request.user.is_staff and not is_leader:
                messages.error(request, "Ошибка удаления: недостаточно прав.")
            else:
                try:
                    for rel in ['climber_members', 'climbs']:
                        try:
                            getattr(group, rel).all().delete()
                        except Exception:
                            pass
                    try:
                        climber_members.objects.filter(groups_id=group).delete()
                    except Exception:
                        pass
                    try:
                        climbs.objects.filter(group_id=group).delete()
                    except Exception:
                        pass

                    group.delete()
                    messages.success(request, "Группа успешно удалена.")
                except Exception as e:
                    messages.error(request, f"Ошибка удаления группы: {e}")

        # 5. Запись в группу
        elif action == 'join_group':
            group_id = request.POST.get('group_id')
            try:
                group = groups.objects.get(id=group_id)
                if climber_members.objects.filter(climber_id=current_climber, groups_id=group).exists():
                    messages.error(request, 'Вы уже записаны в эту группу!')
                elif climber_members.objects.filter(groups_id=group).count() >= group.max_members:
                    messages.error(request, f'Достигнут лимит участников ({group.max_members} макс.)!')
                else:
                    climber_members.objects.create(climber_id=current_climber, groups_id=group, role=False, joined_date=timezone.now())
                    messages.success(request, f'Вы успешно записались в группу "{group.name}"!')
            except Exception as e:
                messages.error(request, f"Ошибка: {e}")

        return redirect('/home/')
        
    all_groups = groups.objects.select_related('mountain_id').all()
    
    for g in all_groups:
        g.safe_date = "Не указана"
        for df in ['date_formation', 'start_event', 'date_start', 'date', 'created_at', 'start_time']:
            if hasattr(g, df) and getattr(g, df):
                g.safe_date = getattr(g, df)
                break
                
        g.safe_difficulty = "Стандарт"
        if g.mountain_id:
            for mf in ['recommended_category', 'recommended_rank', 'razryad', 'category', 'difficulty', 'рекомендуемый_разряд']:
                if hasattr(g.mountain_id, mf) and getattr(g.mountain_id, mf):
                    g.safe_difficulty = getattr(g.mountain_id, mf)
                    break

    all_ascents = []
    try:
        raw_ascents = climbs.objects.all()
        for asc in raw_ascents:
            asc.safe_result = "Успех"
            for rf in ['результат', 'result', 'status', 'success']:
                if hasattr(asc, rf) and getattr(asc, rf) is not None:
                    val = getattr(asc, rf)
                    if isinstance(val, bool):
                        asc.safe_result = "Успех" if val else "Отказ"
                    else:
                        asc.safe_result = str(val)
                    break
                    
            asc.safe_grade = "5"
            for gf in ['оценка', 'grade', 'evaluation', 'score', 'ball']:
                if hasattr(asc, gf) and getattr(asc, gf) is not None:
                    asc.safe_grade = getattr(asc, gf)
                    break
                    
            asc.safe_comment = "Отчёт сохранён"
            for cf in ['комментарий', 'comment', 'description', 'summary']:
                if hasattr(asc, cf) and getattr(asc, cf) is not None:
                    asc.safe_comment = getattr(asc, cf)
                    break

            asc.safe_time = "Не указано"
            for tf in ['date_time_start', 'date_start', 'start_event', 'date', 'datetime', 'start_time']:
                if hasattr(asc, tf) and getattr(asc, tf) is not None:
                    asc.safe_time = getattr(asc, tf)
                    break
                    
            all_ascents.append(asc)
    except Exception:
        all_ascents = []

    user_group_ids = list(climber_members.objects.filter(climber_id=current_climber).values_list('groups_id_id', flat=True))
    all_members = climber_members.objects.select_related('climber_id', 'groups_id').all()
    leader_group_ids = list(climber_members.objects.filter(climber_id=current_climber, role=True).values_list('groups_id_id', flat=True))

    context = {
        'mountains_list': mountains.objects.all(),
        'groups_list': all_groups,
        'user_group_ids': user_group_ids,
        'leader_group_ids': leader_group_ids,
        'current_climber': current_climber,
        'all_members': all_members,
        'all_ascents': all_ascents,
    }
    return render(request, './pages/home.html', context)


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/home/')
    return render(request, './pages/login.html')


def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken!")
            return redirect('/register/')
        
        user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password)
        user.save()
        messages.info(request, "Account created Successfully! Please login.")
        return redirect('/login/')
    return render(request, './pages/register.html')