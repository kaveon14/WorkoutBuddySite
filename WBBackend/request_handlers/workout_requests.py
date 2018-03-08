from WBBackend.models import MainWorkout, SubWorkout, Profile, ExerciseGoals,Workout,WorkoutExercise,Set,CustomExercise,DefaultExercise
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json as json_module
#add function for completeing an workout
@csrf_exempt
def getMainWorkouts(request):
    if request.method == 'POST':
        profileId = request.POST['profileId']
        user_profile = Profile.objects.get(id=profileId)
        mw_list = MainWorkout.objects.filter(user_profile=user_profile)

        default_mw = MainWorkout.objects.get(id=1)
        mw_arr = []
        w = {'id':default_mw.id,'main_workout_name':default_mw.main_workout_name}
        mw_arr.append(w)

        for mw in mw_list:
            w = {'id':mw.id,'main_workout_name':mw.main_workout_name}
            mw_arr.append(w)
        json = {'error':False,'message':'Request successfully completed','RequestResponse':mw_arr}
        return JsonResponse(json)
    
    json = {'error':True,'message':'The http request needs to be "GET" not "POST" ','RequestResponse':None}
    return JsonResponse(json)

@csrf_exempt
def getSubWorkouts(request):     
    if request.method == 'POST':
        mw_id = request.POST['mainWorkoutId']
        mw = MainWorkout.objects.get(id=mw_id)
        sw_list = SubWorkout.objects.filter(mainworkout=mw)
        sw_arr = []
        for sw in sw_list:
            s = {'id':sw.id,'sub_workout_name':sw.sub_workout_name}
            sw_arr.append(s)
        json = {'error':False,'message':'Request successfully completed','RequestResponse':sw_arr}
        return JsonResponse(json)
     
    json = {'error':True,'message':'The http request needs to be "GET" not "POST" ','RequestResponse':None}
    return JsonResponse(json)

@csrf_exempt
def getSubWorkoutExercises(request):#reps and sets are all the same with no ranges
    if request.method == 'GET':
        sw_id = request.GET['subWorkoutId']
        sw = SubWorkout.objects.get(id=sw_id)
        ex_list =  ExerciseGoals.objects.filter(sub_workout=sw)
        ex_arr = []

        for ex in ex_list:
            e = {'id':ex.id,'goal_sets':ex.goal_sets,'goal_reps':ex.goal_reps}
            if ex.default_exercise is None:
                e['exercise_name'] = ex.custom_exercise.exercise_name
                e['exercise_id'] =  ex.custom_exercise.id
                e['default_exercise'] = False
            else:
                e['exercise_name'] = ex.default_exercise.exercise_name
                e['exercise_id'] =  ex.default_exercise.id
                e['default_exercise'] = True
            ex_arr.append(e)

        json = {'error':False,'message':'Request successfully completed','RequestResponse':ex_arr}
        return JsonResponse(json)

    json = {'error':True,'message':'The http request needs to be "GET" not "POST" ','RequestResponse':None}
    return JsonResponse(json)

#clean this up
@csrf_exempt
def getCompletedWorkouts(request):
    if request.method == 'POST':
        profileId = request.POST['profileId']
        profile = Profile.objects.get(id=profileId)
        wk_list = Workout.objects.filter(user_profile=profile)

        we_arr = []
        for wk in wk_list:
            we_list = wk.completed_exercises.all()
            dict = {'id':wk.id,'date':wk.date,'main_workout_name':wk.main_workout_name,'sub_workout_name':wk.sub_workout_name}
            ex_arr = []

            for we in we_list:
                e = {'id':we.id,'exercise_name':we.exercise_name}
                set_list = we.completed_sets.all()
                set_arr = []
                for set in set_list:
                    s = {'id':set.id,'set':set.set,'reps':set.reps,
                         'weight':set.weight,'unit':set.unit}
                    set_arr.append(s)

                e['sets'] = set_arr
                ex_arr.append(e)

            dict['completed_exercises'] = ex_arr
            we_arr.append(dict)

        json = {'error':False,'message':'Request successfully completed','RequestResponse':we_arr}
        return JsonResponse(json)
    json = {'error':True,'message':'The http request needs to be "POST" not "GET" ','RequestResponse':None}
    return JsonResponse(json)

#create sub workouts differently
@csrf_exempt#not right
def createMainWorkout(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        
        profile_id =  json_data['profileId']
        user_profile = Profile.objects.get(id=profile_id)
        main_workout_name =  json_data['main_workout_name']
        main_workout = MainWorkout(main_workout_name=main_workout_name)
        main_workout.save()
        main_workout.user_profile = user_profile
        main_workout.save()
        user_profile.custom_main_workouts.add(main_workout)
        user_profile.save()
        print(main_workout.main_workout_name)
        json = {'error':False,'message':'Request successfully completed','RequestResponse':{'id':main_workout.id}}
        return JsonResponse(json)
    
    json = {'error':True,'message':'The http request needs to be "POST" not "GET" ','RequestResponse':None}
    return JsonResponse(json)

@csrf_exempt
def createSubWorkout(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        
        profile_id = json_data['profileId']
        user_profile = Profile.objects.get(id=profile_id)
        main_workout = MainWorkout.objects.get(id=json_data['mainWorkoutId'])
        sub_workout_name = json_data['sub_workout_name']
        sub_workout = SubWorkout(main_workout=main_workout,sub_workout_name=sub_workout_name)
        sub_workout.save()
        main_workout.sub_workouts.add(sub_workout)
        
        sub_workout.user_profile = user_profile
        sub_workout.save()
        user_profile.custom_sub_workouts.add(sub_workout)
        user_profile.save()
        json = {'error':False,'message':'Request successfully completed','RequestResponse':{'id':sub_workout.id}}
        return JsonResponse(json)
    
    json = {'error':True,'message':'The http request needs to be "POST" not "GET" ','RequestResponse':None}
    return JsonResponse(json)

@csrf_exempt
def setSubWorkoutExercises(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)

        sub_workout_id = json_data['subWorkoutId']
        sub_workout = SubWorkout.objects.get(id=sub_workout_id)

        json_list = json_data['exercise_list']
        default_ex_list = []
        custom_ex_list = []
        for map in json_list:
            if map['default_exercise'] is False:
                ex = CustomExercise.objects.get(id=map['id'])
                custom_ex_list.append(ex)                                
            else: 
                ex = DefaultExercise.objects.get(id=map['id'])
                default_ex_list.append(ex)

        sub_workout.default_exercises.add(*default_ex_list)
        sub_workout.custom_exercises.add(*custom_ex_list)
        sub_workout.save()

        json = {'error':False,'message':'Request successfully completed','RequestResponse':None}
        return JsonResponse(json)
    
    json = {'error':True,'message':'The http request needs to be "POST" not "GET" ','RequestResponse':None}
    return JsonResponse(json)

@csrf_exempt
def deleteMainWorkout(request):#also deletes subworkouts as expected
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        user_profile = Profile.objects.get(id=json_data['profileId'])
        main_workout = MainWorkout.objects.get(id=json_data['id'])
        main_workout.delete(keep_parents=False)
        user_profile.remove(main_workout)
        user_profile.save()
        main_workout = None
        json = {'error':False,'message':'Request successfully completed','RequestResponse':None}
        return JsonResponse(json)
    
    json = {'error':True,'message':'The http request needs to be "POST" not "GET" ','RequestResponse':None}
    return JsonResponse(json)

@csrf_exempt
def deleteSubWorkout(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        sub_workout = SubWorkout.objects.get(id=json_data['id'])
        sub_workout.delete(keep_parents=False)      
        sub_workout = None
        json = {'error':False,'message':'Request successfully completed','RequestResponse':None}
        return JsonResponse(json)
    
    json = {'error':True,'message':'The http request needs to be "POST" not "GET" ','RequestResponse':None}
    return JsonResponse(json)

@csrf_exempt
def updateMainWorkoutName(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        main_workout = MainWorkout.objects.get(id=json_data['id'])
        main_workout.main_workout_name = json_data['main_workout_name']
        main_workout.save()
        json = {'error': False, 'message': 'Request successfully completed', 'RequestResponse': None}
        return JsonResponse(json)

    json = {'error': True, 'message': 'The http request needs to be "POST" not "GET" ', 'RequestResponse': None}
    return JsonResponse(json)

@csrf_exempt
def updateSubWorkoutName(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        sub_workout = SubWorkout.objects.get(id=json_data['id'])
        sub_workout.sub_workout_name = json_data['sub_workout_name']
        sub_workout.save()
        json = {'error': False, 'message': 'Request successfully completed', 'RequestResponse': None}
        return JsonResponse(json)

    json = {'error': True, 'message': 'The http request needs to be "POST" not "GET" ', 'RequestResponse': None}
    return JsonResponse(json)

@csrf_exempt
def updateSubWorkoutExerciseGoals(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        exercise_goals = json_data['exercise_goals']
        for ex in exercise_goals:
            e = ExerciseGoals.objects.get(id=ex.id)
            e.goal_sets = ex.goal_sets
            e.goal_reps = ex.goal_reps
            e.save()

        json = {'error': False, 'message': 'Request successfully completed', 'RequestResponse': None}
        return JsonResponse(json)

    json = {'error': True, 'message': 'The http request needs to be "POST" not "GET" ', 'RequestResponse': None}
    return JsonResponse(json)

@csrf_exempt
def addSubWorkoutExerciseGoals(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json_module.loads(data)
        sub_workout = SubWorkout.objects.get(id=json_data['id'])
        ex_goal = ExerciseGoals(goal_sets=json_data['goal_sets'])
        ex_goal.goal_reps = json_data['goal_reps']
        ex_goal.save()
        if json_data['default_exercise']:
            ex = DefaultExercise.objects.get(id=json_data['exercise_id'])
            ex._goal.default_exercise = ex
        else:
            ex = CustomExercise.objects.get(id=json_data['exercise_id'])
            ex_goal.custom_exercise = ex
        ex_goal.save()

        json = {'error': False, 'message': 'Request successfully completed', 'RequestResponse': None}
        return JsonResponse(json)

    json = {'error': True, 'message': 'The http request needs to be "POST" not "GET" ', 'RequestResponse': None}
    return JsonResponse(json)

@csrf_exempt
def deleteSubWorkoutExerciseGoals(request):
    if request.method == 'POST':
        ex_goal = ExerciseGoals.objects.get(id=request.POST['exercise_goal_id'])
        ex_goal.delete()
        ex_goal = None
        json = {'error': False, 'message': 'Request successfully completed', 'RequestResponse': None}
        return JsonResponse(json)

    json = {'error': True, 'message': 'The http request needs to be "POST" not "GET" ', 'RequestResponse': None}
    return JsonResponse(json)
