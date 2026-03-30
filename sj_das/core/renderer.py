import glm
import moderngl
import numpy as np
from PIL import Image


class FabricRenderer:
    def __init__(self, ctx=None):
        self.ctx = ctx
        if not self.ctx:
            self.ctx = moderngl.create_context(standalone=True)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 Mvp;
                uniform mat4 Model;
                uniform vec3 LightPos;
                uniform vec3 CamPos;
                uniform float Time;

                in vec3 in_position;
                in vec3 in_normal;
                in vec2 in_texcoord;

                out vec3 v_normal;
                out vec3 v_pos;
                out vec2 v_texcoord;
                out vec3 v_light_dir;
                out vec3 v_view_dir;

                void main() {
                    // Saree Drape Warp Effect: 
                    // Create natural folds using multiple sine waves
                    vec3 pos = in_position;
                    float wave = sin(pos.x * 2.5 + Time * 0.5) * 0.15;
                    wave += sin(pos.y * 3.0 + Time * 0.2) * 0.1;
                    
                    // Taper the drape at the top (waist)
                    float taper = smoothstep(1.0, -1.0, pos.y);
                    pos.z += wave * taper;
                    
                    gl_Position = Mvp * vec4(pos, 1.0);
                    v_pos = (Model * vec4(pos, 1.0)).xyz;
                    v_normal = mat3(Model) * in_normal; // Simplified normal for prototype
                    v_texcoord = in_texcoord;
                    v_light_dir = normalize(LightPos - v_pos);
                    v_view_dir = normalize(CamPos - v_pos);
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D Texture;
                uniform vec3 Color;
                uniform float Metallic;
                uniform float Roughness;

                in vec3 v_normal;
                in vec3 v_pos;
                in vec2 v_texcoord;
                in vec3 v_light_dir;
                in vec3 v_view_dir;

                out vec4 f_color;

                void main() {
                    vec3 N = normalize(v_normal);
                    
                    // Simple fake normals for the folds based on position derivatives
                    vec3 dx = dFdx(v_pos);
                    vec3 dy = dFdy(v_pos);
                    N = normalize(cross(dx, dy));

                    vec3 L = normalize(v_light_dir);
                    vec3 V = normalize(v_view_dir);
                    vec3 H = normalize(L + V);

                    vec4 texColor = texture(Texture, v_texcoord);
                    vec3 albedo = texColor.rgb * Color;

                    // PBR approximation for Silk
                    float NdotL = max(dot(N, L), 0.0);
                    float diff = NdotL;
                    
                    float NdotH = max(dot(N, H), 0.0);
                    float spec = pow(NdotH, (1.0 - Roughness) * 256.0);
                    
                    // Silk has strong rim lighting (Fresnel)
                    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);
                    
                    vec3 ambient = albedo * 0.2;
                    vec3 finalColor = ambient + albedo * diff + (vec3(spec) + fresnel * 0.5) * Metallic;

                    // Gamma correction
                    finalColor = pow(finalColor, vec3(1.0/2.2));
                    f_color = vec4(finalColor, 1.0);
                }
            '''
        )

        self.vbo = None
        self.vao = None
        self.ibo = None
        self.texture = None
        self.create_drape_mesh()

    def create_drape_mesh(self):
        """Creates a high-tessellation grid for cloth simulation."""
        res_x, res_y = 64, 64
        vertices = []
        for y in range(res_y):
            for x in range(res_x):
                # Position (-1 to 1)
                px = (x / (res_x - 1)) * 2.0 - 1.0
                py = (y / (res_y - 1)) * 2.0 - 1.0
                pz = 0.0
                # Normals (pointing forward)
                nx, ny, nz = 0.0, 0.0, 1.0
                # UVs (0 to 1)
                u = x / (res_x - 1)
                v = y / (res_y - 1)
                vertices.extend([px, py, pz, nx, ny, nz, u, v])

        indices = []
        for y in range(res_y - 1):
            for x in range(res_x - 1):
                i = y * res_x + x
                indices.extend([i, i + 1, i + res_x])
                indices.extend([i + 1, i + res_x + 1, i + res_x])

        self.vbo = self.ctx.buffer(np.array(vertices, dtype='f4'))
        self.ibo = self.ctx.buffer(np.array(indices, dtype='i4'))

        content = [
            (self.vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_texcoord'),
        ]
        self.vao = self.ctx.vertex_array(self.prog, content, self.ibo)

    def update_texture(self, image_path):
        try:
            img = Image.open(image_path).convert('RGB')
            # Handle both old and new Pillow Transpose constants
            if hasattr(Image, 'Transpose'):
                img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            else:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                
            # Resize internal textures to powers of two for better performance
            img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
            self.texture = self.ctx.texture(img.size, 3, img.tobytes())
            self.texture.build_mipmaps()
            
            # Use safer attribute access for moderngl constants if needed,
            # but LINEAR_MIPMAP_LINEAR is standard in moderngl.
            self.texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        except Exception as e:
            print(f"Failed to load texture: {e}")

    def render(self, width, height, time=0):
        self.ctx.clear(0.05, 0.05, 0.07) # Darker professional bg
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)

        aspect_ratio = width / height
        proj = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)

        # Better camera placement for viewing a saree drape
        cam_dist = 4.0
        cam_x = np.sin(time * 0.3) * cam_dist
        cam_z = np.cos(time * 0.3) * cam_dist
        view = glm.lookAt(glm.vec3(cam_x, 0.5, cam_z),
                          glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))

        model = glm.mat4(1.0)
        # Vertical alignment
        model = glm.rotate(model, glm.radians(-10.0), glm.vec3(1.0, 0.0, 0.0))

        mvp = proj * view * model

        self.prog['Mvp'].write(mvp)
        self.prog['Model'].write(model)
        self.prog['LightPos'].write(glm.vec3(2.0, 5.0, 5.0))
        self.prog['CamPos'].write(glm.vec3(cam_x, 0.5, cam_z))
        self.prog['Time'].value = time
        self.prog['Color'].write(glm.vec3(1.0, 1.0, 1.0))
        self.prog['Metallic'].value = 0.8  # High silk luster
        self.prog['Roughness'].value = 0.3

        if self.texture:
            self.texture.use(0)
            self.prog['Texture'].value = 0

        self.vao.render()
