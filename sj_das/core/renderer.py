import glm
import moderngl
import numpy as np
from PIL import Image


class FabricRenderer:
    def __init__(self, ctx=None):
        self.ctx = ctx
        if not self.ctx:
            # Standalone context if not provided (e.g. for offscreen rendering)
            self.ctx = moderngl.create_context(standalone=True)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 Mvp;
                uniform mat4 Model;
                uniform vec3 LightPos;
                uniform vec3 CamPos;

                in vec3 in_position;
                in vec3 in_normal;
                in vec2 in_texcoord;

                out vec3 v_normal;
                out vec3 v_pos;
                out vec2 v_texcoord;
                out vec3 v_light_dir;
                out vec3 v_view_dir;

                void main() {
                    gl_Position = Mvp * vec4(in_position, 1.0);
                    v_pos = (Model * vec4(in_position, 1.0)).xyz;
                    v_normal = mat3(Model) * in_normal;
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

                const float PI = 3.14159265359;

                void main() {
                    vec3 N = normalize(v_normal);
                    vec3 L = normalize(v_light_dir);
                    vec3 V = normalize(v_view_dir);
                    vec3 H = normalize(L + V);

                    // Base color from texture
                    vec4 texColor = texture(Texture, v_texcoord);
                    vec3 albedo = texColor.rgb * Color;

                    // Simple PBR-like lighting (Cook-Torrance approximation)

                    // Diffuse
                    float NdotL = max(dot(N, L), 0.0);
                    vec3 diffuse = albedo * NdotL;

                    // Specular (Blinn-Phong for simplicity in this prototype)
                    float NdotH = max(dot(N, H), 0.0);
                    float spec = pow(NdotH, (1.0 - Roughness) * 128.0);
                    vec3 specular = vec3(spec) * Metallic;

                    // Ambient
                    vec3 ambient = albedo * 0.1;

                    vec3 finalColor = ambient + diffuse + specular;

                    // Gamma correction
                    finalColor = pow(finalColor, vec3(1.0/2.2));

                    f_color = vec4(finalColor, 1.0);
                }
            '''
        )

        self.vbo = None
        self.vao = None
        self.texture = None
        self.create_plane()

    def create_plane(self):
        # Create a simple plane mesh
        # x, y, z, nx, ny, nz, u, v
        vertices = np.array([
            -1.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            1.0, -1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0,
            1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0,
            -1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
        ], dtype='f4')

        indices = np.array([0, 1, 2, 2, 3, 0], dtype='i4')

        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(indices)

        content = [
            (self.vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_texcoord'),
        ]

        self.vao = self.ctx.vertex_array(self.prog, content, self.ibo)

    def update_texture(self, image_path):
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            self.texture = self.ctx.texture(img.size, 3, img.tobytes())
            self.texture.build_mipmaps()
            self.texture.use()
        except Exception as e:
            print(f"Failed to load texture: {e}")

    def render(self, width, height, time=0):
        self.ctx.clear(0.1, 0.1, 0.1)
        self.ctx.enable(moderngl.DEPTH_TEST)

        aspect_ratio = width / height
        proj = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)

        # Camera orbit
        cam_x = np.sin(time) * 3.0
        cam_z = np.cos(time) * 3.0
        view = glm.lookAt(glm.vec3(cam_x, -2.0, cam_z),
                          glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))

        model = glm.mat4(1.0)
        # Rotate plane to be vertical-ish
        model = glm.rotate(model, glm.radians(90.0), glm.vec3(1.0, 0.0, 0.0))

        mvp = proj * view * model

        self.prog['Mvp'].write(mvp)
        self.prog['Model'].write(model)
        self.prog['LightPos'].write(glm.vec3(5.0, 5.0, 5.0))
        self.prog['CamPos'].write(glm.vec3(cam_x, -2.0, cam_z))
        self.prog['Color'].write(glm.vec3(1.0, 1.0, 1.0))
        self.prog['Metallic'].value = 0.5  # Silk-like
        self.prog['Roughness'].value = 0.4

        if self.texture:
            self.texture.use()

        self.vao.render()
