from robot import TelekomRobot


from flask import Flask, request
from flask import jsonify




app = Flask('Telekom Login Robot')



@app.route('/login', methods=['POST']) #GET requests will be blocked
def login_request():
    req_data = request.get_json()

    email = req_data['email']
    password = req_data['password']

    robot = TelekomRobot()
    success = robot.login(uri=telekom_login_page, email=email, password=password, screenshot=False)

    if success:
        return jsonify(return_code=200, message='login was a success')
    else:
        return jsonify(return_code=503, message='login was a failure')


@app.route('/test', methods=['GET']) #GET requests will be blocked
def tester():
    return jsonify(return_code=200, message='We hit the end point')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000) #run app in debug mode on port 5000