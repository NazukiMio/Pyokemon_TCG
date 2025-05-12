class SceneManager:
    """
    场景管理器类，管理游戏的不同场景之间的切换
    """
    
    def __init__(self, screen):
        """
        初始化场景管理器
        
        Args:
            screen: pygame屏幕对象
        """
        self.screen = screen
        self.current_scene = None
        self.scenes = {}
        self.user_id = None
    
    def add_scene(self, scene_name, scene_class):
        """
        添加场景到管理器
        
        Args:
            scene_name: 场景名称（字符串）
            scene_class: 场景类（类引用）
        """
        self.scenes[scene_name] = scene_class
    
    def change_scene(self, scene_name, *args, **kwargs):
        """
        切换到指定场景
        
        Args:
            scene_name: 要切换到的场景名称
            *args, **kwargs: 传递给场景构造函数的参数
        
        Returns:
            布尔值表示是否成功切换
        """
        if scene_name not in self.scenes:
            print(f"场景 '{scene_name}' 不存在")
            return False
        
        # 创建新场景实例，传入屏幕和回调函数
        self.current_scene = self.scenes[scene_name](
            self.screen, self.handle_scene_callback, *args, **kwargs
        )
        return True
    
    def handle_scene_callback(self, callback_data=None):
        """
        处理来自场景的回调
        
        Args:
            callback_data: 场景返回的回调数据
        """
        if callback_data == "login":
            # 切换到登录场景
            self.change_scene("login")
        elif callback_data == "register":
            # 切换到注册场景
            self.change_scene("register")
        elif callback_data == "main_menu":
            # 切换到主菜单场景
            self.change_scene("main_menu", user_id=self.user_id)
        elif isinstance(callback_data, int) or (isinstance(callback_data, str) and callback_data.isdigit()):
            # 如果回调数据是用户ID，保存它并切换到主菜单
            self.user_id = int(callback_data)
            self.change_scene("main_menu", user_id=self.user_id)
    
    def run(self, initial_scene="login"):
        """
        运行场景管理器，启动初始场景
        
        Args:
            initial_scene: 初始场景名称
        """
        if not self.change_scene(initial_scene):
            raise ValueError(f"无法启动初始场景: {initial_scene}")
        
        # 运行当前场景
        while self.current_scene:
            self.current_scene.run()
            
            # 如果场景运行结束但没有设置新场景，退出循环
            if self.current_scene:
                break