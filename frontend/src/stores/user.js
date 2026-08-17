import { defineStore } from "pinia";
import apiClient from "@/api/client";

// You can name the return value of `defineStore()` anything you want,
// but it's best to use the name of the store and surround it with `use`
// and `Store` (e.g. `useUserStore`, `useCartStore`, `useProductStore`)
// the first argument is a unique id of the store across your application
export const useUserStore = defineStore("user", {
  state: () => ({
    firstname: "FirstName",
    lastname: "LastName",
    email: "someone@someplace.org",
    isAdmin: false,
    isLoggedIn: false,
    avatar: "male_avatar.png",
    id: "",
    user_color: "",
    male: true,
    isChild: false,
  }),
  getters: {
    fullname: state => state.firstname + " " + state.lastname,
    getID: state => state.id,
  },
  actions: {
    loginUser(
      firstname,
      lastname,
      email,
      isAdmin,
      male,
      id,
      user_color,
      groups,
    ) {
      this.firstname = firstname;
      this.lastname = lastname;
      this.email = email;
      this.isAdmin = isAdmin;
      this.isLoggedIn = true;
      this.id = id;
      this.user_color = user_color;
      this.male = male;

      if (groups.includes(1)) {
        this.isChild = true;
      } else {
        this.isChild = false;
      }

      if (male) {
        if (this.isChild) {
          this.avatar = "child_male_avatar.jpg";
        } else {
          this.avatar = "adult_male_avatar.jpg";
        }
      } else {
        if (this.isChild) {
          this.avatar = "child_female_avatar.jpg";
        } else {
          this.avatar = "adult_female_avatar.jpg";
        }
      }
    },
    logoutUser() {
      this.firstname = "FirstName";
      this.lastname = "LastName";
      this.email = "someone@somplace.org";
      this.isAdmin = false;
      this.isLoggedIn = false;
      this.avatar = "male_avatar.jpg";
      this.id = "";
      this.user_color = "";
      this.male = true;
    },
    // Writes through /api/v2/me, which derives the user from the session and
    // takes no id -- so this can only ever edit the logged-in user. The DRF
    // endpoint it replaces (PATCH /api/users/{id}/) was unauthenticated and
    // accepted every model field, is_superuser included.
    //
    // Errors are re-thrown, not swallowed. The previous version caught and
    // discarded them, so ProfileForm reported success on every failed save.
    async updateProfile(user) {
      const response = await apiClient.put("/me", {
        first_name: user.first_name,
        last_name: user.last_name,
        male: user.male,
        user_color: user.user_color,
      });

      // Re-seed from the server's response rather than the submitted form, so
      // any server-side normalisation is reflected. `groups` is passed through:
      // omitting it used to throw TypeError inside loginUser on
      // `groups.includes(1)`, leaving isChild and avatar stale.
      const me = response.data;
      this.loginUser(
        me.first_name,
        me.last_name,
        me.email,
        // is_superuser, matching LoginView -- is_staff here would silently
        // change the user's admin status on every profile save.
        me.is_superuser,
        me.male,
        me.id,
        me.user_color,
        me.groups ?? [],
      );
      return me;
    },
  },
  persist: true,
});
