from multiprocessing import Process, Value, Queue, Manager
class MultiProcess:
    def __init__(self):
        self.manager = Manager()
        self.dropped_connection = Value('i', 0)
        self.image_queue = self.manager.Queue()
        self.image_process = Process(target = self._take_pic)
                
        self.processes = []

    def start(self):
        try:
            time.sleep(1)
            self.image_process.start()

        except Exception as e:
            print(Fore.RED + '[MultiProcess-START ERROR] %s' % str(e))
            raise e

    def _format_for(self, target, message):
        return {
            'target': target,
            'payload': message,
        }
   
    def put_task_in_img_q(self):
        commands = ['task','task2','task3','task4','task5','task6']
        for c in commands:
            self.image_queue.put_nowait(c)
                
    def _take_pic(self):
            # self.sender = imagezmq.ImageSender(connect_to='tcp://192.168.20.25:5555') #Connection to Image Processing Server
            while True:
                try:
                    if not self.image_queue.empty():
                        print("the image queue size is", self.image_queue.qsize())
                        print("the image queue is not empty")
                        q = self.image_queue.get()
                        print("the image queue size after dequeue is", self.image_queue.qsize())
                        print("queue top take_pic():", str(q))

            
                        break
                except Exception as e:
                    print(Fore.RED + '[MultiProcess-PROCESS-IMG ERROR] %s' % str(e))
