<template>
  <div class="doc">
    <h3>Document {{ index + 1 }}</h3>

    <!-- IMAGES -->
    <p><b>Add images (auto-convert)</b></p>
    <input
      type="file"
      multiple
      accept="image/png,image/jpeg"
      @change="autoConvertImages"
    />

    <ul v-if="images.length">
      <li v-for="img in images" :key="img.name">
        🖼️ {{ img.name }}
      </li>
    </ul>


    <!-- PDF -->
    <p><b>OR upload a PDF (auto-save)</b></p>
    <input
      type="file"
      accept="application/pdf"
      @change="autoSavePdf"
    />
  </div>
</template>

<script setup>
import axios from "axios";
import { ref } from "vue";

const props = defineProps({ index: Number });
const emit = defineEmits(["saved"]);

const API_URL = "http://localhost:8000";
const images = ref([]);

/* 🔥 AUTO-CONVERT IMAGES */
async function autoConvertImages(e) {
  const selected = Array.from(e.target.files);
  if (!selected.length) return;

  images.value = selected;

  const form = new FormData();
  selected.forEach(img => form.append("files", img));

  const key =
    `img_${props.index}_` +
    selected.map(i => i.name).join(",");

  const res = await axios.post(
    `${API_URL}/images-to-pdf`,
    form
  );

  emit("saved", res.data.path, key);

  images.value = [];
  e.target.value = "";
}

/* 🔥 AUTO-SAVE PDF */
async function autoSavePdf(e) {
  const file = e.target.files[0];
  if (!file) return;

  const form = new FormData();
  form.append("file", file);

  const key = `pdf_${props.index}_${file.name}`;

  const res = await axios.post(
    `${API_URL}/save-pdf`,
    form
  );

  emit("saved", res.data.path, key);
  e.target.value = "";
}
</script>
